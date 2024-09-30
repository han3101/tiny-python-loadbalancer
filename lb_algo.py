import random
from server import BackendServer
from enum import Enum

class LoadBalancingAlgo(Enum):
    RANDOM = 1
    ROUND_ROBIN = 2
    IP_HASH = 3

class LBAlgo:
    def __init__(self, servers: list[BackendServer], algo_type: LoadBalancingAlgo):
        self.servers = servers
        self.algo_type = algo_type
        self.round_robin_index = 0

    def get_next_server(self, ip: str = None) -> BackendServer:
        """Dispatch to the appropriate algorithm based on the enum."""
        if self.algo_type == LoadBalancingAlgo.RANDOM:
            return self.random_algo()
        elif self.algo_type == LoadBalancingAlgo.ROUND_ROBIN:
            return self.round_robin_algo()
        elif self.algo_type == LoadBalancingAlgo.IP_HASH:
            if ip is None:
                raise ValueError("[IPHashAlgoError] IP is required for IP Hashing")
            return self.ip_hash_algo(ip)
        else:
            raise ValueError("[LBAlgoError] Unknown load balancing algorithm")

    def random_algo(self) -> BackendServer:
        if not self.servers:
            raise ValueError("[RandomAlgoError] No servers available")

        server = random.choice(self.servers)

        return server

    def round_robin_algo(self) -> BackendServer:
        if not self.servers:
            raise ValueError("[RoundRobinAlgoError] No servers available")

        server = self.servers[self.round_robin_index]
        self.round_robin_index = (self.round_robin_index + 1) % len(self.servers)  # Move to next server
        return server

    def ip_hash_algo(self, ip: str) -> BackendServer:
        if not self.servers:
            raise ValueError("[IPHashAlgoError] No servers available")

        index = hash(ip) % len(self.servers)
        server = self.servers[index]

        return server