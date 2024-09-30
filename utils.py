from urllib.parse import urlparse

def extract_host_and_port(url: str):
    parsed_url = urlparse(url)
    
    # Split the netloc to separate host and port
    host = parsed_url.hostname
    port = parsed_url.port
    
    return host, port