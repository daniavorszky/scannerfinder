#!/usr/bin/env python3
"""Serve the reference site in site/ from this computer and open it in the browser.

Started by view-reference-site.command (Mac) and view-reference-site.bat (Windows), or by Claude
when a member asks to see the reference site:  python3 templates/master-reference/view_reference_site.py
The pages use paths that start at the site root, so they need a server; opened as files they show
unstyled. Nothing leaves the computer. Close the window, or press Ctrl+C, to stop.
"""
import functools, http.server, os, socket, sys, threading, webbrowser

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")


def free_port(first=4399, tries=20):
    for port in range(first, first + tries):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return 0   # let the system pick


def main():
    if not os.path.isfile(os.path.join(SITE, "index.html")):
        sys.exit(f"The reference site was not found at {SITE}. Unzip the Blueprint again; the site folder ships inside it.")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE)
    handler.log_message = lambda *a, **k: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", free_port()), handler)
    url = f"http://localhost:{server.server_address[1]}/"
    print(f"Serving the reference site at {url}\nClose this window, or press Ctrl+C, to stop.", flush=True)
    if not os.environ.get("NO_OPEN"):
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
