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
        self.health = ServerStatus.UNHEALTHY
        self.requests_served = 0

    def __str__(self):
        return (f"Server: {self.get_url()}, "
                f"Weight: {self.weight}, "
                f"health: {self.health}, "
                f"Active Connections: {self.active_connections}, "
                f"Failures: {self.failures}")

    def __repr__(self):
        return self.__str__()

    def get_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def get_status(self) -> ServerStatus:
        if self.health == ServerStatus.HEALTHY:
            return "Healthy"
        elif self.health == ServerStatus.UNHEALTHY:
            return "Unhealthy"
        elif self.health == ServerStatus.DEAD:
            return "Dead"

    def set_status(self, status: ServerStatus):
        self.health = status

    def increment_failures(self):
        self.failures += 1
    
    def get_failures(self):
        return self.failures

    def increment_requests_served(self):
        self.requests_served += 1

    def get_stats(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "weight": self.weight,
            "health": self.health,
            "failures": self.failures,
            "requests_served": self.requests_served
        }
    
