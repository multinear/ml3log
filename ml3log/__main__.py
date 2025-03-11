#!/usr/bin/env python3
import argparse
import sys
import time
from ml3log.server import start_server


def main():
    parser = argparse.ArgumentParser(description='ML3Log Server')
    parser.add_argument(
        '--host', default='localhost', help='Host to bind to (default: localhost)'
    )
    parser.add_argument(
        '--port', type=int, default=6020, help='Port to listen on (default: 6020)'
    )

    args = parser.parse_args()

    print(f"Starting ML3Log server at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop")

    # Start the server
    start_server(address=args.host, port=args.port)

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down ML3Log server...")
        sys.exit(0)


if __name__ == "__main__":
    main()
