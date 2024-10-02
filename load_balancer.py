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
        self.config = config
        self.healthy_servers = healthy_servers
        self.unhealthy_servers = []
        self.total_requests_served = 0

        print(self.backend_servers)

        self.lb_algo = LBAlgo(servers, healthy_servers, config['lb_method'])
        self.app = self.create_app()
        self.healthchecker = HealthCheck(servers, healthy_servers, config)


    def create_app(self) -> FastAPI:
        app = FastAPI()

        @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def proxy(full_path: str, request: Request):
            client_ip = request.client.host
            server = self.get_next_server(ip=client_ip)
            
            retry_limit = self.config["retries"]

            # Prepare the request parameters
            method = request.method
            headers = dict(request.headers)
            query_params = dict(request.query_params)
            
            # Read the body for POST/PUT requests
            body = await request.body()

            timeout = httpx.Timeout(
            connect=self.config['connect_timeout'],
            read=self.config['read_timeout'],
            write=self.config['send_timeout'],
            pool=self.config['next_timeout']
            )

            # Use httpx to forward the request to the backend server
            retry = 0
            while retry <= retry_limit:
                url = f"{server.get_url()}/{full_path}"
                print(f"Proxying request to {url}")
                
                async with httpx.AsyncClient(timeout=timeout) as client:

                    # for _ in range(retry_limit):
                    
                    try: 
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

                        elif response.status_code in [500, 502, 503, 504]:
                            retry += 1
                            print(f"Server {server.get_url()} returned {response.status_code}. Switching to another server.")
                            if self.lb_algo.get_algo() == "ip-hash":
                                self.lb_algo.update_algo("round-robin")
                            server = self.get_next_server(ip=client_ip)
                            self.lb_algo.update_algo(self.config['lb_method'])

                            print(f"Switched to new server: {server.get_url()}")
                            continue
                        else:
                            break

                    except httpx.RequestError as e:
                        retry += 1
                        print(f"Network error: {e}. Switching to another server.")
                        if self.lb_algo.get_algo() == "ip-hash":
                            self.lb_algo.update_algo("round-robin")
                        server = self.get_next_server(ip=client_ip)
                        self.lb_algo.update_algo(self.config['lb_method'])
                        
                        print(f"Switched to new server: {server.get_url()}")

                

            raise HTTPException(status_code=500, detail="All retries failed on all servers.")

        return app

    def get_next_server(self, ip: str = None) -> BackendServer:
        if not self.healthy_servers:
            raise HTTPException(status_code=503, detail="No healthy servers available.")

        server = self.lb_algo.get_next_server(ip=ip)
        while server not in self.healthy_servers and self.healthy_servers:
            server = self.lb_algo.get_next_server(ip=ip)
        
        return server

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
        self.healthchecker.initial_health_screen()
        health_check_task = asyncio.create_task(self.start_healthchecks())
        uvicorn_config = uvicorn.Config(app=self.app, host="0.0.0.0", port=self.port)
        uvicorn_server = uvicorn.Server(uvicorn_config)
        print("Starting Uvicorn server...")
        await uvicorn_server.serve()
