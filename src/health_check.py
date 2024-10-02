import httpx, asyncio
from server import BackendServer
from typing import List, Set

class HealthCheck:
    def __init__(self, servers: List[BackendServer], healthy_servers: Set[BackendServer], config: dict):

        self.servers = servers
        self.healthy_servers = healthy_servers
        self.interval = config['health_check_interval']
        self.timeout = config['health_check_timeout']
        self.fails = config['health_check_fails']
        self.passes = config['health_check_pass']


        self.server_status = {server: {"healthy": True, "fail_count": 0, "pass_count": 0} for server in servers}

    async def check_server(self, server):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{server.get_url()}/health", timeout=self.timeout)
                if response.status_code == 200:
                    print(f"Server {server.get_url()} is healthy")
                    return True
                return False
                print(f"Server {server.get_url()} is unhealthy")
        except (httpx.RequestError, httpx.TimeoutException):
            print(f"Server {server.get_url()} is unavailable")
            return False

    async def perform_health_check(self, server):
       
        is_healthy = await self.check_server(server)
        if is_healthy:
            self.server_status[server]["fail_count"] = 0
            self.server_status[server]["pass_count"] += 1
            # Mark as healthy if it passes enough checks
            if self.server_status[server]["pass_count"] >= self.passes and server not in self.healthy_servers:
                self.server_status[server]["healthy"] = True
                self.healthy_servers.add(server)
        else:
            self.server_status[server]["fail_count"] += 1
            self.server_status[server]["pass_count"] = 0
            # Mark as unhealthy if it fails enough checks
            if self.server_status[server]["fail_count"] >= self.fails and server in self.healthy_servers:
                self.server_status[server]["healthy"] = False
                self.healthy_servers.remove(server)

    async def run_health_checks(self):
        while True:
            tasks = [self.perform_health_check(server) for server in self.servers]
            await asyncio.gather(*tasks)
            # Wait for the next round of health checks
            await asyncio.sleep(self.interval)

            # print("Healthy Servers: ", self.get_healthy_servers())

    def get_healthy_servers(self):
        return [server for server, status in self.server_status.items() if status["healthy"]]

    def initial_health_screen(self):
        for server in self.servers:
            try:
                response = httpx.get(f"{server.get_url()}/health", timeout=0.5)
                
                if response.status_code == 200:
                    self.healthy_servers.add(server)

            except httpx.TimeoutException:
                print(f"[TIMEOUT] {server} did not respond in time.")
            except httpx.RequestError as exc:
                print(f"[ERROR] Error occurred while requesting {server}: {exc}")
