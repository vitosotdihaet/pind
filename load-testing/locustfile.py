import random
import string

import config
import psycopg
from locust import HttpUser, events


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
target_host = ""


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
        target_host

    CONFIG = config.load_config(path=environment.parsed_options.config_path)

    index_type = environment.parsed_options.index_type
    op_type = environment.parsed_options.operation
    intensity_key = f"intensity_{op_type}_{index_type.upper()}"

    SEARCH_ENDPOINT = f"/search_{index_type}"
    INSERT_ENDPOINT = f"/insert_{index_type}"
    REQUESTS_PER_SECOND = getattr(CONFIG, intensity_key)
    ROW_SIZE = CONFIG.row_size

    hosts = fetch_hosts(
        psql_address=environment.parsed_options.psql_address,
        admin_password=environment.parsed_options.admin_password,
    )
    if not hosts:
        raise RuntimeError("No HTTP peer addresses found in _pico_peer_address")

    if environment.runner:
        worker_index = getattr(environment.runner, "worker_index", 0)
        if worker_index is None or worker_index < 0:
            worker_index = 0
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


def random_key(size_bytes: int) -> str:
    """Return a random string of exactly `size_bytes` ASCII letters."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=size_bytes))


def search_task(user: HttpUser):
    payload = {"fk": random_key(ROW_SIZE)}  # pyright: ignore[reportArgumentType]
    user.client.post(SEARCH_ENDPOINT, json=payload)


def insert_task(user: HttpUser):
    payload = {
        "pk": random_key(ROW_SIZE),  # pyright: ignore[reportArgumentType]
        "fk": random_key(ROW_SIZE),  # pyright: ignore[reportArgumentType]
        "sk": random_key(ROW_SIZE),  # pyright: ignore[reportArgumentType]
    }
    user.client.post(INSERT_ENDPOINT, json=payload)


class LoadUser(HttpUser):
    host = ""

    def wait_time(self):
        if self.environment.runner and self.environment.runner.user_count:
            rate_per_user = REQUESTS_PER_SECOND / self.environment.runner.user_count
            return 1.0 / rate_per_user if rate_per_user > 0 else 0
        return 0
