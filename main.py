import config, lb_algo, load_balancer, server, utils

def main():
    config_data = config.load_config()
    config.validate_config(config_data)

    # debug
    print(config_data)

    servers = []

    for srv in config_data['upstream']:
        host, port = utils.extract_host_and_port(srv['domain'])
        weight = srv.get('weight', 1)
        
        backend_server = server.BackendServer(host, port, weight)
        servers.append(backend_server)

    lb = load_balancer.LoadBalancer(servers, config_data, config_data['listen'])

    lb.run()

if __name__ == "__main__":
    main()