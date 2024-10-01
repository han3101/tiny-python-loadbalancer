from enum import Enum

class ServerStatus(Enum):
    HEALTHY = 1
    UNHEALTHY = 2
    DEAD = 3

class BackendServer:
    def __init__(self, host, port, weight=1):
        self.host = host
        self.port = port
        self.weight = weight
        self.active_connections = 0
        self.failures = 0
        self.health = ServerStatus.HEALTHY
        self.requests_served = 0

    def __str__(self):
        return (f"Server: {self.get_url()}, "
                f"Weight: {self.weight}, "
                f"Active Connections: {self.active_connections}, "
                # f"Health Status: {self.health_status.value}, "
                f"Failures: {self.failures}")

    def __repr__(self):
        return self.__str__()

    def get_url(self):
        return f"http://{self.host}:{self.port}"
    
