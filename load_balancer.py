from fastapi import FastAPI, HTTPException, Request
import asyncio
import uvicorn
from typing import List
from pydantic import BaseModel
from server import BackendServer
from lb_algo import LBAlgo

class LoadBalancer:
    def __init__(self, servers: List[BackendServer], config: dict, port: int = 80):
        self.backend_servers = servers
        self.port = port
        self.healthy_servers = []

        print(self.backend_servers)

        self.lb_algo = LBAlgo(servers, config['lb_method'])
        self.app = self.create_app()


    def create_app(self) -> FastAPI:
        app = FastAPI()

        @app.get("/")
        async def root(request: Request):
            server = await self.lb_algo.get_next_server()
            return {"message": "Hello World", "server": server.get_url()}

        return app


    def get_backend_server(self) -> BackendServer:
        return self.lb_algo.get_next_server()

    def print_backend_stats(self):
        print("Backend Stats:")
        for server in self.backend_servers:
            print(f"Server: {server.url}, Requests Served: {server.requests_served}, Status: {server.get_status()}")

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)