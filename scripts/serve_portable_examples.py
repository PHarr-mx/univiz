#!/usr/bin/env python3
"""Local-only preview server: ?policy=static blocks JS; ?policy=offline blocks remote resources."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import argparse


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        policy = parse_qs(urlsplit(self.path).query).get('policy', ['normal'])[0]
        if policy in {'static', 'offline'}:
            script = "'none'" if policy == 'static' else "'unsafe-inline'"
            self.send_header('Content-Security-Policy',
                             f"default-src 'none'; style-src 'unsafe-inline'; "
                             f"script-src {script}; img-src 'self' data:; "
                             "font-src 'self'; base-uri 'none'")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    examples = Path(__file__).resolve().parents[1] / 'examples'
    handler = partial(Handler, directory=str(examples))
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
        print(f'Preview: http://127.0.0.1:{args.port}/', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
