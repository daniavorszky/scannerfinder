# Local preview server for the price-tools prototype: python3 serve.py [port]
import http.server, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8795
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=ROOT, **k)
http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
