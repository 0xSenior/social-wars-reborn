import os
import sys
import argparse

from server.infrastructure.config import ServerConfig
from server import create_app


def parse_arguments() -> ServerConfig:
    parser = argparse.ArgumentParser(description="Social Wars Reborn - Clean Server Engine")
    parser.add_argument("--host", "--ip", dest="host", default="127.0.0.1", help="Host/IP address to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", dest="port", type=int, default=5055, help="Port to listen on (default: 5055)")
    parser.add_argument("--public-url", dest="public_url", default=None, help="Public URL when behind reverse proxy")
    args = parser.parse_args()

    return ServerConfig(
        host=args.host,
        port=args.port,
        public_url=args.public_url
    )


def setup_console_title():
    if os.name == 'nt':
        os.system("color")
        os.system("title Social Wars Reborn Server")
    else:
        sys.stdout.write("\x1b]2;Social Wars Reborn Server\x07")


def main():
    setup_console_title()
    config = parse_arguments()
    app = create_app(config)
    print(f" [*] Social Wars Reborn Server online at {config.resolved_public_url}")
    app.run(host=config.host, port=config.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
