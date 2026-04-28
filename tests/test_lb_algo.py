import os
import subprocess
import sys
from itertools import permutations
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from lb_algo import LBAlgo
from server import BackendServer


@pytest.fixture
def servers():
    return [
        BackendServer("backend-a", 8080),
        BackendServer("backend-b", 8080),
        BackendServer("backend-c", 8080),
    ]


def test_stable_hash_returns_known_value():
    assert LBAlgo._stable_hash("192.168.1.1") == 6787661676840164395


def test_stable_hash_is_consistent_across_python_hash_seeds():
    hash_value_seed_one = _run_stable_hash_in_subprocess("1")
    hash_value_seed_two = _run_stable_hash_in_subprocess("999")

    assert hash_value_seed_one == "6787661676840164395"
    assert hash_value_seed_one == hash_value_seed_two


def test_ip_hash_server_selection_is_consistent_for_any_server_order(servers):
    selected_urls = set()

    for ordered_servers in permutations(servers):
        algo = LBAlgo(list(ordered_servers), set(ordered_servers), "ip-hash")
        selected_urls.add(algo.get_next_server(ip="192.168.1.1").get_url())

    assert selected_urls == {"http://backend-a:8080"}


def test_ip_hash_sorts_by_hash_ring_position_before_bisecting(servers, monkeypatch):
    algo = LBAlgo(servers, set(servers), "ip-hash")
    hash_values = {
        "http://backend-a:8080": 30,
        "http://backend-b:8080": 10,
        "http://backend-c:8080": 20,
        "client-ip": 15,
        "wrap-around-client": 35,
    }

    monkeypatch.setattr(
        LBAlgo,
        "_stable_hash",
        staticmethod(lambda value: hash_values[value]),
    )

    assert algo.ip_hash_algo("client-ip").get_url() == "http://backend-c:8080"
    assert algo.ip_hash_algo("wrap-around-client").get_url() == "http://backend-b:8080"


def _run_stable_hash_in_subprocess(python_hash_seed: str) -> str:
    script = (
        "import sys; "
        f"sys.path.insert(0, {str(SRC_DIR)!r}); "
        "from lb_algo import LBAlgo; "
        "print(LBAlgo._stable_hash('192.168.1.1'))"
    )
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = python_hash_seed

    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return completed.stdout.strip()
