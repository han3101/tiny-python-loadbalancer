import random, bisect
from server import BackendServer
from enum import Enum
from typing import List, Set

class LoadBalancingAlgo(Enum):
    RANDOM = 1
    ROUND_ROBIN = 2
    IP_HASH = 3

algo_map = {
    "random": LoadBalancingAlgo.RANDOM,
    "round-robin": LoadBalancingAlgo.ROUND_ROBIN,
    "ip-hash": LoadBalancingAlgo.IP_HASH
}

class LBAlgo:
    def __init__(self, servers: List[BackendServer], healthy_servers: Set[BackendServer], algo_type: str):
        
        algo_type_str = algo_type.lower().strip()
        if algo_type_str not in algo_map:
            raise ValueError(f"[LBAlgoError] Unsupported algorithm type: {algo_type_str}, please enter either 'random', 'round-robin' or 'ip-hash'")
        
        self.servers = servers
        self.healthy_servers = healthy_servers
        self.algo_type = algo_map[algo_type_str]
        self.round_robin_index = 0

    def get_next_server(self, ip: str = None) -> BackendServer:
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

    # Not optimized for large number of servers
    # Use only for small number of servers
    def ip_hash_algo(self, ip: str) -> BackendServer:
        if not self.healthy_servers:
            raise ValueError("[IPHashAlgoError] No servers available")

        healthy_servers_list = sorted(self.healthy_servers, key=lambda s: s.get_url())

        ip_hash = hash(ip)
        server_index = bisect.bisect_right([hash(s.get_url()) for s in healthy_servers_list], ip_hash) % len(healthy_servers_list)

        server = healthy_servers_list[server_index]

        return server

    def update_algo(self, algo_type: str) -> None:
        algo_type_str = algo_type.lower().strip()
        if algo_type_str not in algo_map:
            raise ValueError(f"[LBAlgoError] Unsupported algorithm type: {algo_type_str}, please enter either 'random', 'round-robin' or 'ip-hash'")
        
        self.algo_type = algo_map[algo_type_str]


    def get_algo(self) -> str:
        for algo_str, algo_enum in algo_map.items():
            if algo_enum == self.algo_type:
                return algo_str

        raise ValueError("[LBAlgoError] No matching algorithm string found for the current algo_type.")