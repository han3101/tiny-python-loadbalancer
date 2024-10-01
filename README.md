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

# TODO:
1. Implement graceful reloading for configuration updates
2. Dockerise loadbalancer