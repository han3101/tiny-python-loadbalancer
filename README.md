# tiny-python-loadbalancer

Tiny python loadbalancer is a multi-process, event driven load balancer modeled after NginX that supports random, ip-hashing and round robin distribution, health checks, alerts, retries and failover 

**If you are running it directly on your local machine, update config.json to localhost**
To start, create a virtual environment in Mac and Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies, update config.json and you are good to run the program
```bash
pip install -r requirements.txt
cd src
python3 main.py
```

**Unit Tests**
Run tests from the repository root after installing dependencies.
```bash
pytest -v
```

If you prefer not to activate the virtual environment, run pytest through the venv interpreter directly.
```bash
.venv/bin/python -m pytest -v
```

**If you are running it on docker**
```bash
docker build -t python-lb .
docker run -p 80:80 -p 3030 python-lb
```

**Debugging and Diagnostics**
There is a separate diagnostic and debugging server on port 3030 to get statistics on the loadbalancer and the backend servers

**Load Balancing Algorithims**
3 supported algorithms currently
1. random --> :white_check_mark: Optimized for large number of servers
2. round-robin --> :white_check_mark: Optimized for large number of servers
3. ip-hash --> :exclamation: Not optimized for large number of servers, use only for less than 50 servers!
    * Uses consistent hashing algorithm

**Local testing**
Start the sample backend servers from the repository root in separate terminals.
```bash
python3 backend/backend.py --port 8081
python3 backend/backend.py --port 8082
python3 backend/backend.py --port 8083
```

There is a small client runner at `run_script/request_runner.py` that sends requests through the load balancer and prints which backend port handled each request.
```bash
python3 run_script/request_runner.py --base-url http://localhost
python3 run_script/request_runner.py --base-url http://localhost --method POST
```

To test sticky routing by client IP locally, set `"lb_method": "ip-hash"` in `config.json`, start the backend servers, start the load balancer, and then send requests with simulated client IPs:
```bash
python3 run_script/request_runner.py \
  --base-url http://localhost \
  --client-ips 10.0.0.1,10.0.0.2,10.0.0.1,10.0.0.3 \
  --requests 9
```

Requests with the same simulated client IP should consistently map to the same backend port.


# TODO:
1. Implement graceful reloading for configuration updates
