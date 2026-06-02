import os
import random
import string
from collections import defaultdict
from pathlib import Path
from threading import Lock

import matplotlib
import numpy as np

matplotlib.use("Agg")  # headless backend
import config
import matplotlib.pyplot as plt
import psycopg
from locust import HttpUser, events, task
from locust.runners import MasterRunner, WorkerRunner


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument(
        "--config-path", required=True, help="Path to configuration file"
    )
    parser.add_argument(
        "--index-type", choices=["gsi", "lsi"], required=True, help="gsi or lsi"
    )
    parser.add_argument(
        "--operation",
        choices=["search", "insert"],
        required=True,
        help="search or insert",
    )
    parser.add_argument(
        "--admin-password", required=True, help="Admin password of Picodata"
    )
    parser.add_argument(
        "--psql-address",
        required=True,
        help="psql address of Picodata",
    )


CONFIG = config.LoadTestingConfig.default()
SEARCH_ENDPOINT = ""
INSERT_ENDPOINT = ""
REQUESTS_PER_SECOND = ""
ROW_SIZE = ""
OPERATION = ""
TIMEOUT = 0

PREFILL_RATIO = 0.8


def prefill_database(
    host: str,
    insert_endpoint: str,
    pk_sk_pool: list[tuple[str, str]],
    fk_pool: list[str],
    ratio: float,
):
    """Insert `ratio` fraction of the pk/sk pool into the DB via HTTP."""
    import requests

    n = int(len(pk_sk_pool) * ratio)
    if n <= 0:
        return

    url = f"{host}{insert_endpoint}"
    print(f"Prefilling {n}/{len(pk_sk_pool)} rows into {url} ...")

    session = requests.Session()
    sample = random.sample(pk_sk_pool, n)

    failures = 0
    for i, (pk, sk) in enumerate(sample, 1):
        fk = random.choice(fk_pool)
        try:
            resp = session.post(url, json={"pk": pk, "fk": fk, "sk": sk}, timeout=10)
            if resp.status_code >= 400:
                failures += 1
        except Exception:
            failures += 1
        if i % 1000 == 0:
            print(f"  prefilled {i}/{n} (failures: {failures})")

    print(f"Prefill complete: {n - failures}/{n} succeeded, {failures} failures")


PK_SK_POOL: list[tuple[str, str]] = []
FK_POOL: list[str] = []


def generate_key_pools(row_size: int, data_cardinality: int, fk_cardinality: int):
    """Pre-generate fixed pools of keys to respect cardinality constraints."""
    global PK_SK_POOL, FK_POOL
    rng = random.Random(42)
    PK_SK_POOL = [
        (
            "".join(rng.choices(string.ascii_letters + string.digits, k=row_size)),
            "".join(rng.choices(string.ascii_letters + string.digits, k=row_size)),
        )
        for _ in range(data_cardinality)
    ]
    FK_POOL = [
        "".join(rng.choices(string.ascii_letters + string.digits, k=row_size))
        for _ in range(fk_cardinality)
    ]
    print(
        f"Generated {len(PK_SK_POOL)} pk/sk pairs and {len(FK_POOL)} fk values "
        f"(row_size={row_size} bytes)"
    )


RESPONSE_TIMES: dict[str, list[float]] = defaultdict(list)
RESPONSE_TIMES_LOCK = Lock()


@events.request.add_listener
def on_request(
    request_type,  # pyright: ignore[reportUnusedParameter]
    name,
    response_time,
    response_length,  # pyright: ignore[reportUnusedParameter]
    exception,
    context,  # pyright: ignore[reportUnusedParameter]
    **kwargs,  # pyright: ignore[reportUnusedParameter]
):
    # don't save failed requests
    if exception is not None:
        return
    with RESPONSE_TIMES_LOCK:
        RESPONSE_TIMES[name].append(response_time)


def save_histogram(name: str, times: list[float], out_dir: Path):
    if not times:
        return

    arr = np.array(times, dtype=float)

    # clip at p99.1 so a few outliers don't squash the plot
    upper = np.percentile(arr, 99.1)
    clipped = arr[arr <= upper]

    # Freedman–Diaconis rule for bin width
    if len(clipped) > 1:
        iqr = np.subtract(*np.percentile(clipped, [75, 25]))
        bin_width = 2 * iqr / (len(clipped) ** (1 / 3)) if iqr > 0 else 0
        bins = (
            max(20, int(np.ceil((clipped.max() - clipped.min()) / bin_width)))
            if bin_width > 0
            else 50
        )
        bins = min(bins, 200)
    else:
        bins = 20

    fig, ax = plt.subplots(figsize=(9, 5))
    counts, edges, _ = ax.hist(
        clipped, bins=bins, edgecolor="blue", color="#FFFFFF00", alpha=0.5
    )

    # annotate key percentiles
    for pct, color in [(50, "#65743A"), (95, "#DFAD4D"), (99, "#DBDA55")]:
        val = np.percentile(arr, pct)
        ax.axvline(
            val,
            color=color,
            linestyle="--",
            linewidth=1,
            label=f"p{pct} = {val:.1f} мс",
        )

    graph_name = "unknown"
    match name:
        case "/search_gsi":
            graph_name = "поиске в ГВИ"
        case "/search_lsi":
            graph_name = "поиске в ЛВИ"
        case "/insert_gsi":
            graph_name = "обновлении ГВИ"
        case "/insert_lsi":
            graph_name = "обновлении ЛВИ"

    ax.set_title(
        f"Распределение времени ожидания ответа БД при {graph_name}\n"
        f"Всего запросов: {len(arr)}, мин={arr.min():.1f} мс, макс={arr.max():.1f} мс"
    )

    ax.axvline(
        arr.mean(),
        color="r",
        linestyle="--",
        linewidth=1.5,
        label=f"Медиана = {arr.mean():.1f} мс",
    )

    std_val = arr.std()
    mean_val = arr.mean()
    if mean_val - std_val >= 0:
        ax.axvline(
            mean_val - std_val,
            color="green",
            linestyle=":",
            linewidth=1.5,
        )
    ax.axvline(
        mean_val + std_val,
        color="green",
        linestyle=":",
        linewidth=1.5,
        label=f"±1σ, где σ  = {std_val:.1f} мс",
    )

    x_step = np.repeat(edges, 2)[1:-1]
    y_step = np.repeat(counts, 2)

    ax.fill_between(
        x_step,
        0,
        y_step,
        where=((x_step >= mean_val - std_val) & (x_step <= mean_val + std_val)),
        color="green",
        alpha=0.25,
        step="mid",
    )

    ax.set_xlabel("Время, мс")
    ax.set_ylabel("Количество запросов")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    safe_name = name.strip("/")
    png_path = os.path.join(out_dir, f"hist_{safe_name}.png")
    csv_path = os.path.join(out_dir, f"hist_{safe_name}.csv")

    fig.savefig(png_path, dpi=120)
    plt.close(fig)

    with open(csv_path, "w") as f:
        f.write("bin_left_ms,bin_right_ms,count\n")
        for i, c in enumerate(counts):
            f.write(f"{edges[i]:.3f},{edges[i + 1]:.3f},{int(c)}\n")

    print(f"[histogram] saved to '{png_path}' ({len(arr)} samples)")


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    # only the master (or standalone) should write output to avoid duplicates
    runner = environment.runner
    if (
        runner is not None
        and getattr(runner, "worker_index", None) is not None
        and getattr(runner, "worker_index", -1) >= 0
        and runner.__class__.__name__ == "WorkerRunner"
    ):
        return

    out_dir = Path(environment.parsed_options.config_path).parent.resolve()

    with RESPONSE_TIMES_LOCK:
        snapshot = {k: list(v) for k, v in RESPONSE_TIMES.items()}

    for name, times in snapshot.items():
        save_histogram(name, times, out_dir)


@events.init.add_listener
def setup_messaging(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner):

        def on_samples(environment, msg, **_):
            with RESPONSE_TIMES_LOCK:
                for name, times in msg.data.items():
                    RESPONSE_TIMES[name].extend(times)

        environment.runner.register_message("rt_samples", on_samples)

    if isinstance(environment.runner, WorkerRunner):
        import gevent

        def report_loop():
            while True:
                gevent.sleep(5)
                with RESPONSE_TIMES_LOCK:
                    payload = {k: v[:] for k, v in RESPONSE_TIMES.items()}
                    RESPONSE_TIMES.clear()
                if payload:
                    environment.runner.send_message("rt_samples", payload)

        gevent.spawn(report_loop)


def fetch_hosts(psql_address: str, admin_password: str) -> list[str]:
    """Fetch HTTP addresses of all cluster nodes from _pico_peer_address."""
    host, port = psql_address.rsplit(":", 1)

    with psycopg.connect(
        host=host,
        port=int(port),
        user="admin",
        password=admin_password,
        dbname="postgres",
        sslmode="disable",
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT address FROM _pico_peer_address WHERE connection_type = 'http'"
            )
            rows = cur.fetchall()

    return [f"http://{row[0]}" for row in rows]


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global \
        CONFIG, \
        SEARCH_ENDPOINT, \
        INSERT_ENDPOINT, \
        REQUESTS_PER_SECOND, \
        ROW_SIZE, \
        OPERATION, \
        TIMEOUT

    CONFIG = config.load_config(path=environment.parsed_options.config_path)
    TIMEOUT = CONFIG.timeout

    OPERATION = environment.parsed_options.operation
    index_type = environment.parsed_options.index_type
    intensity_key = f"intensity_{OPERATION}_{index_type.upper()}"

    SEARCH_ENDPOINT = f"/search_{index_type}"
    INSERT_ENDPOINT = f"/insert_{index_type}"
    REQUESTS_PER_SECOND = getattr(CONFIG, intensity_key)
    ROW_SIZE = CONFIG.row_size

    generate_key_pools(
        row_size=ROW_SIZE,
        data_cardinality=CONFIG.data_cardinality,
        fk_cardinality=CONFIG.fk_cardinality,
    )

    hosts = fetch_hosts(
        psql_address=environment.parsed_options.psql_address,
        admin_password=environment.parsed_options.admin_password,
    )
    if not hosts:
        raise RuntimeError("No HTTP peer addresses found in _pico_peer_address")

    runner = environment.runner
    is_worker = isinstance(runner, WorkerRunner)
    is_master_or_standalone = not is_worker  # MasterRunner or LocalRunner

    # Prefill DB only once from master only for search tests
    if OPERATION == "search" and is_master_or_standalone:
        prefill_database(
            host=hosts[0],
            insert_endpoint=INSERT_ENDPOINT,
            pk_sk_pool=PK_SK_POOL,
            fk_pool=FK_POOL,
            ratio=PREFILL_RATIO,
        )

    if is_worker:
        worker_index = getattr(runner, "worker_index", 0) or 0
    else:
        worker_index = 0

    if OPERATION == "search":
        LoadUser.tasks = [search_task]
    else:
        LoadUser.tasks = [insert_task]

    target_host = hosts[worker_index % len(hosts)]
    LoadUser.host = target_host
    environment.host = target_host
    print(f"Worker {worker_index} will target {target_host}")
    # print(f"Target rate: {REQUESTS_PER_SECOND} req/s, key size: {ROW_SIZE} bytes")


def search_task(user: HttpUser):
    fk = random.choice(FK_POOL)
    payload = {"fk": fk}
    user.client.post(SEARCH_ENDPOINT, json=payload, timeout=TIMEOUT)


def insert_task(user: HttpUser):
    pk, sk = random.choice(PK_SK_POOL)
    fk = random.choice(FK_POOL)
    payload = {"pk": pk, "fk": fk, "sk": sk}
    user.client.post(INSERT_ENDPOINT, json=payload, timeout=TIMEOUT)


class LoadUser(HttpUser):
    host = None

    def on_start(self):
        if not self.host:
            self.host = self.environment.host

    @task
    def run_op(self):
        global OPERATION
        if OPERATION == "search":
            search_task(self)
        else:
            insert_task(self)
