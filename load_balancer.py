from fastapi import FastAPI, HTTPException, Request
import asyncio
import uvicorn, httpx
from typing import List, Set
from pydantic import BaseModel
from server import BackendServer
from lb_algo import LBAlgo
from health_check import HealthCheck

class LoadBalancer:
    def __init__(self, servers: List[BackendServer], healthy_servers: Set[BackendServer], config: dict, port: int = 80):
        self.backend_servers = servers
        self.port = port
        self.healthy_servers = []
        self.unhealthy_servers = []
        self.total_requests_served = 0

        print(self.backend_servers)

        self.lb_algo = LBAlgo(servers, config['lb_method'])
        self.app = self.create_app()
        self.healthchecker = HealthCheck(servers, healthy_servers, config)


    def create_app(self) -> FastAPI:
        app = FastAPI()

        # @app.get("/")
        # async def root(request: Request):
        #     server = self.lb_algo.get_next_server()
        #     # return {"message": "Hello World", "server": server.get_url()}

        #     try:
        #         async with httpx.AsyncClient() as client:
        #             response = await client.get(server.get_url())
        #             if response.status_code == 200:
        #                 server.requests_served += 1
        #                 server.total_requests_served += 1
        #                 return response.json()
        #             else:
        #                 raise HTTPException(status_code=response.status_code)
        #             return response.json()
        #     except httpx.HTTPError as e:
        #         raise HTTPException(status_code=500, detail=f"Error connecting to {server.get_url()}: {str(e)}")

        @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def proxy(full_path: str, request: Request):
            # Build the complete URL by combining backend URL and the requested path
            server = self.lb_algo.get_next_server()
            url = f"{server.get_url()}/{full_path}"
            print(f"Proxying request to {url}")

            # Prepare the request parameters
            method = request.method
            headers = dict(request.headers)
            query_params = dict(request.query_params)
            
            # Read the body for POST/PUT requests
            body = await request.body()

            # Use httpx to forward the request to the backend server
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method=method, 
                        url=url,
                        headers=headers,
                        params=query_params,
                        content=body
                    )
                    if response.status_code == 200:
                        server.requests_served += 1
                        self.total_requests_served += 1

                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.text
                }
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Error connecting to {server.get_url()}: {str(e)}")

        return app


    def get_backend_server(self) -> BackendServer:
        return self.lb_algo.get_next_server()

    def print_backend_stats(self):
        print("Backend Stats:")
        for server in self.backend_servers:
            print(f"Server: {server.url}, Requests Served: {server.requests_served}, Status: {server.get_status()}")

    async def start_healthchecks(self):
        await self.healthchecker.run_health_checks()

    # def run(self):
    #     uvicorn.run(self.app, host="0.0.0.0", port=self.port)

    async def run(self):

        health_check_task = asyncio.create_task(self.start_healthchecks())
        uvicorn_config = uvicorn.Config(app=self.app, host="0.0.0.0", port=self.port)
        uvicorn_server = uvicorn.Server(uvicorn_config)
        print("Starting Uvicorn server...")
        await uvicorn_server.serve() 
