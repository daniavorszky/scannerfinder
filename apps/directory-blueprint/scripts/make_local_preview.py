#!/usr/bin/env python3
"""Make a copy of the built site that opens by double-clicking index.html.

The built site in dist/ uses paths that start at the domain root (/_astro/x.css, /directory/florida/miami/).
That is right for the live site and for a local server, and wrong for a file opened straight
from disk: the stylesheet is not found and every link leads nowhere. This script writes a
second copy with relative paths and the stylesheet inside each page. The copy is for looking at, never for deploying.

Usage:
  python3 scripts/make_local_preview.py output/<slug>/site/dist output/<slug>/preview
"""
import os, re, shutil, sys

ATTR = re.compile(r'\b(href|src|action)="(/[^"/][^"]*|/)"')
CSS_URL = re.compile(r"url\((['\"]?)/(?!/)")
SHEET = re.compile(r'<link rel="stylesheet" href="(/[^"]+\.css)"\s*/?>')


def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    src, out = sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/")
    if not os.path.isfile(os.path.join(src, "index.html")):
        print(f"ERROR: {src}/index.html not found. Run npm run build first."); sys.exit(1)
    if os.path.isdir(out): shutil.rmtree(out)
    shutil.copytree(src, out)
    pages = links = missing = 0
    for root, _, files in os.walk(out):
        depth = os.path.relpath(root, out)
        up = "" if depth == "." else "../" * (depth.count(os.sep) + 1)
        for f in files:
            p = os.path.join(root, f)
            if f.endswith(".css"):
                t = open(p, encoding="utf-8").read()
                open(p, "w", encoding="utf-8").write(CSS_URL.sub(lambda m: f"url({m.group(1)}{up}", t))
                continue
            if not f.endswith(".html"): continue
            t = open(p, encoding="utf-8").read()

            # The stylesheet goes into the page itself, so the page is styled even in a viewer
            # that shows one file and loads nothing else. Fonts stay as files and fall back
            # to the system fonts named in the tokens when they cannot be loaded.
            def inline(m):
                css = open(os.path.join(src, m.group(1).lstrip("/")), encoding="utf-8").read()
                return "<style>" + CSS_URL.sub(lambda u: f"url({u.group(1)}{up}", css) + "</style>"
            t = SHEET.sub(inline, t)

            def fix(m):
                nonlocal links, missing
                attr, url = m.group(1), m.group(2)
                path, sep, tail = url.partition("?")
                frag = ""
                if "#" in path: path, _, frag = path.partition("#")
                target = path.lstrip("/")
                if path.endswith("/"): target += "index.html"
                if not os.path.exists(os.path.join(out, target)): missing += 1
                links += 1
                return f'{attr}="{up}{target}{"#" + frag if frag else ""}{sep}{tail}"'

            open(p, "w", encoding="utf-8").write(ATTR.sub(fix, t))
            pages += 1
    note = os.path.join(out, "READ-THIS-FIRST.txt")
    open(note, "w").write("This folder is a copy of the site for looking at on your own computer.\n"
                          "Open index.html. Do not upload this folder. The folder to deploy is site/dist.\n")
    print(f"pages rewritten: {pages}, links rewritten: {links}, links whose target is missing: {missing}")
    print(f"open {os.path.join(out, 'index.html')}")


if __name__ == "__main__":
    main()
