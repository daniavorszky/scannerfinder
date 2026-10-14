#!/usr/bin/env python3
"""Reads the mail worker's review queue, sends a draft, ignores an item, or triages one again.

  python3 scripts/mail_inbox.py --slug <slug>                       # new items, readable
  python3 scripts/mail_inbox.py --slug <slug> --status all --json   # everything, raw
  python3 scripts/mail_inbox.py --slug <slug> --send <id> [--text-file reply.txt]   # send the draft (or the file's text) to the sender
  python3 scripts/mail_inbox.py --slug <slug> --ignore <id>         # close without replying
  python3 scripts/mail_inbox.py --slug <slug> --retriage <id>       # match and triage again (after a matcher or prompt change)

--slug may be left out when output/ holds exactly one directory with a worker. The worker's address comes from its
wrangler.jsonc (WORKER_URL) and its key from the secret store scripts/mail_worker.py keeps (`<worker-name>-key`);
MAIL_WORKER_URL and MAIL_WORKER_KEY in the environment override both. The key is never printed.
"""
import argparse, glob, json, os, sys, textwrap, urllib.error, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mail_worker import ROOT, load_secret, read_jsonc  # noqa: E402


def find_worker(slug):
    if slug:
        p = os.path.join(ROOT, "output", slug, "worker", "wrangler.jsonc")
        if not os.path.exists(p): sys.exit(f"no worker at output/{slug}/worker")
        return p
    found = glob.glob(os.path.join(ROOT, "output", "*", "worker", "wrangler.jsonc"))
    if len(found) != 1: sys.exit("say which directory: --slug <slug>")
    return found[0]


def call(url, key, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, method="POST" if body else "GET",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "directory-mail-inbox/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"the worker answered {e.code} for {url.split('?')[0]}: {e.read()[:300].decode('utf-8', 'ignore')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug"); ap.add_argument("--status", default="new"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--done"); ap.add_argument("--ignore"); ap.add_argument("--send"); ap.add_argument("--text-file"); ap.add_argument("--retriage")
    a = ap.parse_args()
    cfg = read_jsonc(find_worker(a.slug))
    base = (os.environ.get("MAIL_WORKER_URL") or cfg["vars"].get("WORKER_URL") or "").rstrip("/")
    key = os.environ.get("MAIL_WORKER_KEY") or load_secret(f"{cfg['name']}-key")
    if not base: sys.exit("the worker has no WORKER_URL yet: run scripts/mail_worker.py setup first")
    if not key: sys.exit(f"no inbox key saved as {cfg['name']}-key: run scripts/mail_worker.py setup on this computer")
    if a.send:
        body = {"status": "send"}
        if a.text_file: body["text"] = open(a.text_file, encoding="utf-8").read()
        print(call(f"{base}/inbox/{a.send}", key, body)); return
    if a.retriage:
        print(call(f"{base}/inbox/{a.retriage}", key, {"status": "retriage"})); return
    if a.done or a.ignore:
        print(call(f"{base}/inbox/{a.done or a.ignore}", key, {"status": "done" if a.done else "ignored"})); return
    items = call(f"{base}/inbox?status={a.status}", key)
    if a.json: print(json.dumps(items, indent=1, ensure_ascii=False)); return
    if not items: print(f"nothing with status '{a.status}'"); return
    for it in items:
        t = it.get("triage") or {}
        print(f"\n== {it['id']}  {it['received'][:16]}  [{it['status']}]  {it['source']}  from {it['from']}\n   {it['subject']}")
        if it.get("triage_error"): print(f"   triage failed: {it['triage_error']}")
        if t:
            c = t["checks"]
            print(f"   {t['category']} ({t['confidence']:.2f})  listing: {t['matched_slug'] or 'none'}  in directory: {c['business_in_directory']}  "
                  f"email matches site: {c['email_domain_matches_website']}  phone matches: {c['phone_matches_listing']}")
            print("   " + textwrap.fill(t["summary"], 110, subsequent_indent="   "))
            if t["missing"]: print("   missing: " + "; ".join(t["missing"]))
            if t["draft_reply"]: print("   draft reply:\n" + textwrap.indent(t["draft_reply"], "     | "))
        else: print("   (triage pending)")


if __name__ == "__main__":
    main()
