import os
import random
import string
from collections import defaultdict
from threading import Lock

import matplotlib
import numpy as np

matplotlib.use("Agg")  # headless backend
import config
import matplotlib.pyplot as plt
import psycopg
from locust import HttpUser, events
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


_response_times: dict[str, list[float]] = defaultdict(list)
_response_times_lock = Lock()


@events.request.add_listener
def on_request(
    request_type,
    name,
    response_time,
    response_length,
    exception,
    context,
    **kwargs,
):
    # skip failed requests if you only want successful latencies
    if exception is not None:
        return
    with _response_times_lock:
        _response_times[name].append(response_time)


def _save_histogram(name: str, times: list[float], out_dir: str):
    if not times:
        return

    arr = np.array(times, dtype=float)

    # use a sensible upper bound (clip at p99.9 so a few outliers don't squash the plot)
    upper = np.percentile(arr, 99.9)
    clipped = arr[arr <= upper]

    # Freedman–Diaconis rule for bin width; fall back to 50 bins
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

    fig, ax = plt.subplots(figsize=(10, 6))
    counts, edges, _ = ax.hist(clipped, bins=bins, edgecolor="black", alpha=0.75)

    # annotate key percentiles
    for pct, color in [(50, "green"), (95, "orange"), (99, "red")]:
        val = np.percentile(arr, pct)
        ax.axvline(
            val,
            color=color,
            linestyle="--",
            linewidth=1.2,
            label=f"p{pct} = {val:.1f} ms",
        )

    ax.set_title(
        f"Response time histogram — {name}\n"
        f"n={len(arr)}, mean={arr.mean():.1f} ms, "
        f"min={arr.min():.1f}, max={arr.max():.1f}"
    )
    ax.set_xlabel("Response time (ms)")
    ax.set_ylabel("Count")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    safe_name = name.strip("/").replace("/", "_") or "root"
    png_path = os.path.join(out_dir, f"hist_{safe_name}.png")
    csv_path = os.path.join(out_dir, f"hist_{safe_name}.csv")

    fig.savefig(png_path, dpi=120)
    plt.close(fig)

    # Also dump raw bin data so you can re-plot later
    with open(csv_path, "w") as f:
        f.write("bin_left_ms,bin_right_ms,count\n")
        for i, c in enumerate(counts):
            f.write(f"{edges[i]:.3f},{edges[i + 1]:.3f},{int(c)}\n")

    print(f"[histogram] saved {png_path} ({len(arr)} samples)")


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    # Only the master (or standalone) should write output to avoid duplicates
    runner = environment.runner
    if (
        runner is not None
        and getattr(runner, "worker_index", None) is not None
        and getattr(runner, "worker_index", -1) >= 0
        and runner.__class__.__name__ == "WorkerRunner"
    ):
        return

    out_dir = os.environ.get("LOCUST_HIST_DIR", "load-testing/results")
    os.makedirs(out_dir, exist_ok=True)

    with _response_times_lock:
        snapshot = {k: list(v) for k, v in _response_times.items()}

    for name, times in snapshot.items():
        _save_histogram(name, times, out_dir)


@events.init.add_listener
def setup_messaging(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner):

        def on_samples(environment, msg, **_):
            with _response_times_lock:
                for name, times in msg.data.items():
                    _response_times[name].extend(times)

        environment.runner.register_message("rt_samples", on_samples)

    if isinstance(environment.runner, WorkerRunner):
        import gevent

        def report_loop():
            while True:
                gevent.sleep(5)
                with _response_times_lock:
                    payload = {k: v[:] for k, v in _response_times.items()}
                    _response_times.clear()
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
    global CONFIG, SEARCH_ENDPOINT, INSERT_ENDPOINT, REQUESTS_PER_SECOND, ROW_SIZE

    CONFIG = config.load_config(path=environment.parsed_options.config_path)

    index_type = environment.parsed_options.index_type
    op_type = environment.parsed_options.operation
    intensity_key = f"intensity_{op_type}_{index_type.upper()}"

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
    if op_type == "search" and is_master_or_standalone:
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

    if op_type == "search":
        LoadUser.tasks = [search_task]
    else:
        LoadUser.tasks = [insert_task]

    target_host = hosts[worker_index % len(hosts)]
    LoadUser.host = target_host
    print(f"Worker {worker_index} will target {target_host}")
    print(f"Target rate: {REQUESTS_PER_SECOND} req/s, key size: {ROW_SIZE} bytes")


def search_task(user: HttpUser):
    fk = random.choice(FK_POOL)
    payload = {"fk": fk}
    user.client.post(SEARCH_ENDPOINT, json=payload)


def insert_task(user: HttpUser):
    pk, sk = random.choice(PK_SK_POOL)
    fk = random.choice(FK_POOL)
    payload = {"pk": pk, "fk": fk, "sk": sk}
    user.client.post(INSERT_ENDPOINT, json=payload)


class LoadUser(HttpUser):
    host = ""
