"""Run with: python run_script/request_runner.py --base-url http://localhost"""

import argparse
import asyncio
import json
import re


PORT_PATTERN = re.compile(r"server\s+(\d+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send requests through the load balancer and print which backend port handled them."
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost",
        help="Load balancer base URL. Defaults to http://localhost.",
    )
    parser.add_argument(
        "--path",
        default="/",
        help="Request path to hit on the load balancer. Defaults to /.",
    )
    parser.add_argument(
        "--method",
        default="GET",
        choices=["GET", "POST"],
        help="HTTP method to use. Defaults to GET.",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=9,
        help="Number of requests to send. Defaults to 9.",
    )
    parser.add_argument(
        "--body",
        default='{"source":"run_script"}',
        help="Request body to send for POST requests. Defaults to a small JSON payload string.",
    )
    parser.add_argument(
        "--client-ips",
        help=(
            "Comma-separated client IPs to send via X-Forwarded-For for ip-hash testing, "
            "for example 10.0.0.1,10.0.0.2,10.0.0.1."
        ),
    )
    return parser.parse_args()


def normalize_path(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def extract_backend_port(payload: dict) -> str:
    headers = payload.get("headers") or {}
    header_port = headers.get("x-backend-port") or headers.get("X-Backend-Port")
    if header_port:
        return str(header_port)

    content = payload.get("content", "")
    try:
        nested = json.loads(content)
        message = nested.get("message", "")
    except json.JSONDecodeError:
        message = content

    match = PORT_PATTERN.search(message)
    return match.group(1) if match else "unknown"


async def send_requests(
    base_url: str,
    path: str,
    method: str,
    request_count: int,
    body: str,
    client_ips: list[str] | None = None,
) -> None:
    try:
        import httpx
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "httpx is not installed in the active environment. Run `pip install -r requirements.txt` first."
        ) from exc

    url = f"{base_url.rstrip('/')}{normalize_path(path)}"
    counts: dict[str, int] = {}

    async with httpx.AsyncClient(timeout=10.0) as client:
        for request_number in range(1, request_count + 1):
            headers = {"content-type": "application/json"} if method == "POST" else {}
            client_ip = None
            if client_ips:
                client_ip = client_ips[(request_number - 1) % len(client_ips)]
                headers["x-forwarded-for"] = client_ip

            response = await client.request(
                method=method,
                url=url,
                content=body if method == "POST" else None,
                headers=headers or None,
            )
            response.raise_for_status()

            payload = response.json()
            backend_port = extract_backend_port(payload)
            counts[backend_port] = counts.get(backend_port, 0) + 1

            print(
                f"request {request_number}: {method} {normalize_path(path)} "
                f"{f'(client ip {client_ip}) ' if client_ip else ''}"
                f"-> backend port {backend_port}"
            )

    print("\nsummary:")
    for backend_port, served_count in sorted(counts.items()):
        print(f"port {backend_port}: {served_count} request(s)")


def main() -> None:
    args = parse_args()
    client_ips = None
    if args.client_ips:
        client_ips = [ip.strip() for ip in args.client_ips.split(",") if ip.strip()]

    asyncio.run(
        send_requests(
            base_url=args.base_url,
            path=args.path,
            method=args.method,
            request_count=args.requests,
            body=args.body,
            client_ips=client_ips,
        )
    )


if __name__ == "__main__":
    main()
