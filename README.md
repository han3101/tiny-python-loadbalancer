# tiny-python-loadbalancer

Tiny python loadbalancer is a multi-process, event driven load balancer modeled after NginX that supports random, ip-hashing and round robin distribution, health checks, alerts, retries and failover 

To start, create a virtual environment in Mac and Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies, update config.json and you are good to run the program
```bash
pip install -r requirements.txt
python3 main.py
```

**Load Balancing Algorithims**
3 supported algorithms currently
1. random --> :white_check_mark: Optimized for large number of servers
2. round-robin --> :white_check_mark: Optimized for large number of servers
3. ip-hash --> :exclamation: Not optimized for large number of servers, use only for less than 50 servers!
    * Uses consistent hashing algorithm


# TODO:
1. Implement graceful reloading for configuration updates
2. Dockerise loadbalancer