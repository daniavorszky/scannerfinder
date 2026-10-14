#!/usr/bin/env python3
"""The directory's mail worker: save the key, check it, set the worker up, redeploy it, wire the claim form.

  python3 scripts/mail_worker.py keys --slug <slug>                 # print the Terminal command(s) the member runs to save the key
  python3 scripts/mail_worker.py save-key anthropic --slug <slug>   # the member runs this in their own Terminal: asks for the key (hidden), tests it, saves it
  python3 scripts/mail_worker.py save-key cloudflare --slug <slug>  # only for a member who deploys with an API token instead of `wrangler login`
  python3 scripts/mail_worker.py check --slug <slug>                # says whether the saved key(s) work, without printing them
  python3 scripts/mail_worker.py setup --slug <slug> --review-to <email> [--name <worker-name>] [--account-id <id>] [--forward-to <email>]
                                                                    # copy templates/worker, fill wrangler.jsonc from site.json, listings.json,
                                                                    # KV namespace, secrets, deploy, record WORKER_URL, send one test claim
  python3 scripts/mail_worker.py deploy --slug <slug>               # after a listings change: refresh listings.json and deploy again
  python3 scripts/mail_worker.py wire-form --slug <slug>            # point site.json's claim form at the worker's /claim (then Gate 5 and deploy the site)

Where the secrets live: on a Mac in the keychain (items `anthropic-<worker-name>`, `<worker-name>-key`, `<worker-name>-url`, and
`cloudflare-<worker-name>` when a token is used); elsewhere in ~/.directory-blueprint/secrets.json (owner-only file).
Nothing is ever written into this folder, printed, or asked for in the chat. Deploys use the `wrangler login` from Gate 6
unless CLOUDFLARE_API_TOKEN is set or a token was saved with `save-key cloudflare`.
"""
import argparse, getpass, json, os, platform, re, secrets as pysecrets, shutil, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
WIN = platform.system() == "Windows"
PY = "python" if WIN else "python3"
NPX = "npx.cmd" if WIN else "npx"


# ---------- secret store ----------

def _file_store():
    return os.path.join(os.path.expanduser("~"), ".directory-blueprint", "secrets.json")


def load_secret(item):
    """The saved value, or an empty string."""
    if platform.system() == "Darwin":
        r = subprocess.run(["security", "find-generic-password", "-s", item, "-w"], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    p = _file_store()
    if not os.path.exists(p):
        return ""
    return json.load(open(p, encoding="utf-8")).get(item, "")


def save_secret(item, value):
    if platform.system() == "Darwin":
        r = subprocess.run(["security", "add-generic-password", "-U", "-a", os.environ.get("USER", "me"), "-s", item, "-w", value],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"could not save {item} to the keychain: {r.stderr.strip()}")
        return "the Mac keychain"
    p = _file_store()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    data = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    data[item] = value
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1)
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass
    return p


# ---------- the key checks ----------

def check_anthropic(key):
    req = urllib.request.Request("https://api.anthropic.com/v1/models", headers={"x-api-key": key, "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200, "the key answers"
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return False, "Anthropic answered 401: that is not a working key (if it starts with cfat_ it is a Cloudflare token, pasted at the wrong prompt)"
        return False, f"Anthropic answered {e.code}"
    except urllib.error.URLError as e:
        return False, f"could not reach api.anthropic.com: {e.reason}"


def check_cloudflare(token):
    req = urllib.request.Request("https://api.cloudflare.com/client/v4/user/tokens/verify", headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            ok = json.loads(r.read()).get("success")
            return bool(ok), "the token verifies" if ok else "Cloudflare did not accept the token"
    except urllib.error.HTTPError as e:
        return False, f"Cloudflare answered {e.code}: not a working token (a key starting with sk-ant- is the Anthropic key, pasted at the wrong prompt)"
    except urllib.error.URLError as e:
        return False, f"could not reach api.cloudflare.com: {e.reason}"


# ---------- config ----------

def worker_dir(slug):
    return os.path.join(ROOT, "output", slug, "worker")


def site_dir(slug):
    return os.path.join(ROOT, "output", slug, "site")


def read_jsonc(path):
    text = open(path, encoding="utf-8").read()
    text = re.sub(r"^\s*//.*$", "", text, flags=re.M)
    return json.loads(text)


def write_config(path, cfg):
    head = ("// Mail worker config, written by scripts/mail_worker.py from the site's site.json. Secrets are set with wrangler\n"
            "// secret put and never appear here. SEND_FROM stays on the root domain (a mail. subdomain bounces replies).\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(head + json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")


def worker_name_for(slug, cfg=None):
    if cfg and not cfg["name"].startswith("REPLACE"):
        return cfg["name"]
    return re.sub(r"[^a-z0-9-]", "-", slug.lower()).strip("-")[:50] + "-mail"


def load_config(slug):
    p = os.path.join(worker_dir(slug), "wrangler.jsonc")
    if not os.path.exists(p):
        sys.exit(f"no worker at output/{slug}/worker yet: run  {PY} scripts/mail_worker.py setup --slug {slug} --review-to <email>")
    return p, read_jsonc(p)


def wrangler_env(name, account_id=None):
    env = dict(os.environ)
    token = env.get("CLOUDFLARE_API_TOKEN") or load_secret(f"cloudflare-{name}")
    if token:
        env["CLOUDFLARE_API_TOKEN"] = token
    if account_id:
        env["CLOUDFLARE_ACCOUNT_ID"] = account_id
    return env


def wrangler(args, cwd, env, input_text=None, quiet=False):
    r = subprocess.run([NPX, "wrangler", *args], cwd=cwd, env=env, input=input_text, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        if "Authentication error" in out or "10000" in out:
            sys.exit("wrangler: authentication error. Either run `npx wrangler login` in the worker folder (the login from Gate 6, "
                     "in the Cloudflare account that holds the directory), or save a token with `save-key cloudflare` made in that account.\n" + out[-1500:])
        sys.exit(f"wrangler {' '.join(args)} failed:\n{out[-3000:]}")
    if not quiet:
        print(out.strip()[-1200:])
    return out


# ---------- commands ----------

def cmd_keys(a):
    name = worker_name_for(a.slug, read_jsonc(os.path.join(worker_dir(a.slug), "wrangler.jsonc")) if os.path.exists(os.path.join(worker_dir(a.slug), "wrangler.jsonc")) else None)
    script = os.path.abspath(__file__)
    print("Run this in your own Terminal. It asks for the key after it starts, so run it first, then copy the key and paste it at the prompt (the paste stays hidden):")
    print()
    print(f'  {PY} "{script}" save-key anthropic --slug {a.slug}')
    print()
    print(f"It tests the key with Anthropic and saves it as `anthropic-{name}`. Deploys use your `wrangler login` from Gate 6.")
    print("Only if you deploy with an API token instead (two Cloudflare accounts, for example), also run:")
    print()
    print(f'  {PY} "{script}" save-key cloudflare --slug {a.slug}')
    print()
    print("That token needs Account permissions Workers Scripts: Edit and Workers KV Storage: Edit (plus Cloudflare Pages: Edit for the site), made in the account that holds the directory.")


def cmd_save_key(a):
    name = worker_name_for(a.slug, read_jsonc(os.path.join(worker_dir(a.slug), "wrangler.jsonc")) if os.path.exists(os.path.join(worker_dir(a.slug), "wrangler.jsonc")) else None)
    if not sys.stdin.isatty():
        sys.exit("run this in your own Terminal, not from Claude Code: it asks for the key and hides what you paste")
    if a.which == "anthropic":
        value = getpass.getpass("Paste the Anthropic API key (starts with sk-ant-), then press Return. It stays hidden: ").strip()
        ok, why = check_anthropic(value)
        item = f"anthropic-{name}"
    else:
        value = getpass.getpass("Paste the Cloudflare API token, then press Return. It stays hidden: ").strip()
        ok, why = check_cloudflare(value)
        item = f"cloudflare-{name}"
    if not value:
        sys.exit("nothing pasted; run the command again")
    if not ok:
        sys.exit(f"not saved: {why}. Copy the key again and run the command again.")
    where = save_secret(item, value)
    print(f"saved as `{item}` in {where} ({why}). Now tell Claude Code: the key is saved.")


def cmd_check(a):
    cfg = None
    p = os.path.join(worker_dir(a.slug), "wrangler.jsonc")
    if os.path.exists(p):
        cfg = read_jsonc(p)
    name = worker_name_for(a.slug, cfg)
    problems = 0
    key = load_secret(f"anthropic-{name}")
    if not key:
        print(f"anthropic-{name}: not saved. The member runs  {PY} scripts/mail_worker.py save-key anthropic --slug {a.slug}  in their Terminal."); problems += 1
    else:
        ok, why = check_anthropic(key)
        print(f"anthropic-{name}: {'ok' if ok else 'FAILS'}, {why}")
        problems += 0 if ok else 1
    token = os.environ.get("CLOUDFLARE_API_TOKEN") or load_secret(f"cloudflare-{name}")
    if token:
        ok, why = check_cloudflare(token)
        print(f"cloudflare-{name}: {'ok' if ok else 'FAILS'}, {why}")
        problems += 0 if ok else 1
    else:
        r = subprocess.run([NPX, "wrangler", "whoami"], cwd=ROOT, capture_output=True, text=True)
        logged = "You are logged in" in (r.stdout + r.stderr)
        print("cloudflare: " + ("the wrangler login from Gate 6 is active" if logged else "no wrangler login and no token. Run `npx wrangler login` (Gate 6) first."))
        problems += 0 if logged else 1
    if load_secret(f"{name}-key"):
        print(f"{name}-key and {name}-url: saved (the review queue is reachable from scripts/mail_inbox.py)")
    sys.exit(1 if problems else 0)


def fill_from_site(slug, cfg, review_to, forward_to, name):
    sj = os.path.join(site_dir(slug), "src", "data", "site.json")
    if not os.path.exists(sj):
        sys.exit(f"no site at output/{slug}/site: Gate 5 has to run before the worker is set up")
    site = json.load(open(sj, encoding="utf-8"))
    domain = site["domain"].strip().lower().removeprefix("https://").removeprefix("http://").strip("/")
    if domain in ("", "example.com"):
        sys.exit("site.json still has the placeholder domain; the worker needs the real one")
    tiers = site.get("tiers", {})
    tier_text = (f"Featured placement on the city page: {tiers.get('city', {}).get('price', '$29 a month')}. "
                 f"Premium listing (verified badge, photos, fuller profile): {tiers.get('premium', {}).get('price', '$97 a year')}. "
                 f"Best-of placement: {tiers.get('bestOf', {}).get('price', 'one time, price on request')}. The listing itself is free.")
    niche = site["niche"]
    noise = set()
    for w in (niche.get("singular", "") + " " + niche.get("plural", "") + " " + niche.get("title", "") + " " + site["state"]["name"]).lower().split():
        w = re.sub(r"[^a-z'&-]", "", w)
        if len(w) > 3:
            noise.add(w)
    cfg["name"] = name
    v = cfg["vars"]
    v["BRAND"] = site["brand"]
    v["SITE_URL"] = f"https://{domain}"
    v["MAIL_ADDRESS"] = f"hello@{domain}"
    v["SEND_FROM"] = f"hello@{domain}"
    v["REVIEW_TO"] = review_to
    v["FORWARD_TO"] = forward_to or ""
    v["TIERS"] = tier_text
    v["NICHE_PLURAL"] = niche.get("plural", "businesses")
    v["STATE_NAME"] = site["state"]["name"]
    v["NAME_NOISE"] = ",".join(sorted(noise))
    return cfg


def refresh_listings(slug):
    csv_path = os.path.join(site_dir(slug), "src", "data", "listings.csv")
    out = os.path.join(worker_dir(slug), "src", "listings.json")
    r = subprocess.run([PY, os.path.join(SCRIPTS, "make_worker_listings.py"), csv_path, out], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("listings.json could not be written:\n" + r.stderr)
    print(r.stdout.strip())


def cmd_setup(a):
    wd = worker_dir(a.slug)
    if not os.path.exists(wd):
        shutil.copytree(os.path.join(ROOT, "templates", "worker"), wd, ignore=shutil.ignore_patterns("node_modules", ".wrangler"))
        print(f"copied templates/worker to output/{a.slug}/worker")
    cfg_path, cfg = load_config(a.slug)
    name = a.name or worker_name_for(a.slug, cfg)
    cfg = fill_from_site(a.slug, cfg, a.review_to, a.forward_to, name)
    if a.account_id:
        cfg["account_id"] = a.account_id
    write_config(cfg_path, cfg)
    print(f"wrangler.jsonc filled: {name}, {cfg['vars']['MAIL_ADDRESS']}, reviews to {a.review_to}")
    refresh_listings(a.slug)

    key = load_secret(f"anthropic-{name}")
    if not key:
        sys.exit(f"the Anthropic key is not saved yet. The member runs, in their own Terminal:\n  {PY} scripts/mail_worker.py save-key anthropic --slug {a.slug}")
    ok, why = check_anthropic(key)
    if not ok:
        sys.exit(f"the saved Anthropic key does not work ({why}); the member runs save-key again")

    env = wrangler_env(name, a.account_id)
    if not os.path.exists(os.path.join(wd, "node_modules")):
        r = subprocess.run(["npm.cmd" if WIN else "npm", "install", "--no-audit", "--no-fund"], cwd=wd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("npm install failed in the worker folder:\n" + r.stderr[-2000:])
        print("npm install done")

    if cfg["kv_namespaces"][0]["id"].startswith("REPLACE"):
        out = wrangler(["kv", "namespace", "create", "INBOX"], wd, env, quiet=True)
        m = re.search(r'"id":\s*"([0-9a-f]{32})"', out) or re.search(r"id\s*=\s*\"?([0-9a-f]{32})", out)
        if not m:
            sys.exit("could not read the new KV namespace id from wrangler's output:\n" + out[-1500:])
        cfg["kv_namespaces"][0]["id"] = m.group(1)
        write_config(cfg_path, cfg)
        print(f"KV namespace INBOX created ({m.group(1)[:8]}...)")

    inbox_key = load_secret(f"{name}-key")
    if not inbox_key:
        inbox_key = pysecrets.token_hex(24)
        save_secret(f"{name}-key", inbox_key)
        print(f"inbox key generated and saved as {name}-key")
    wrangler(["secret", "put", "ANTHROPIC_API_KEY"], wd, env, input_text=key + "\n", quiet=True)
    wrangler(["secret", "put", "INBOX_KEY"], wd, env, input_text=inbox_key + "\n", quiet=True)
    print("secrets set on the worker (ANTHROPIC_API_KEY, INBOX_KEY)")

    out = wrangler(["deploy"], wd, env, quiet=True)
    m = re.search(r"https://[a-z0-9.-]+\.workers\.dev", out)
    if not m:
        sys.exit("deployed, but the worker's address was not in wrangler's output:\n" + out[-1500:])
    url = m.group(0).rstrip("/")
    if cfg["vars"].get("WORKER_URL") != url:
        cfg["vars"]["WORKER_URL"] = url
        write_config(cfg_path, cfg)
        wrangler(["deploy"], wd, env, quiet=True)     # second deploy carries WORKER_URL, which the review links use
    save_secret(f"{name}-url", url)
    print(f"deployed: {url}")

    # one test claim, no acknowledgement to anyone; the review email goes to REVIEW_TO
    data = urllib.parse.urlencode({"business": "Setup test", "name": "Directory Blueprint", "email": a.review_to, "phone": "",
                                   "changes": "This is the setup test from scripts/mail_worker.py. Ignore it.", "_noack": "1"}).encode()
    try:
        urllib.request.urlopen(urllib.request.Request(f"{url}/claim", data=data, method="POST"), timeout=30)
    except urllib.error.HTTPError as e:
        if e.code not in (301, 302, 303):
            sys.exit(f"the test claim was refused: {e.code}")
    item = None
    for _ in range(12):
        time.sleep(5)
        try:
            req = urllib.request.Request(f"{url}/inbox?status=new", headers={"Authorization": f"Bearer {inbox_key}"})
            items = json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception:
            continue
        item = next((i for i in items if i.get("subject", "").startswith("Claim form: Setup test")), None)
        if item and (item.get("triage") or item.get("triage_error")):
            break
    if not item:
        sys.exit("the test claim did not appear in the queue; read the live log with `npx wrangler tail` in the worker folder and send one again")
    if item.get("triage_error"):
        print(f"test claim queued, but triage failed: {item['triage_error']}. A new ANTHROPIC_API_KEY can take a minute to roll out; retriage with  {PY} scripts/mail_inbox.py --slug {a.slug} --retriage {item['id']}")
    else:
        t = item["triage"]
        print(f"test claim triaged: {t['category']} (confidence {t['confidence']:.2f}); the review email is on its way to {a.review_to}. Ignore it with  {PY} scripts/mail_inbox.py --slug {a.slug} --ignore {item['id']}")
    print(f"\nNext: in the Cloudflare dashboard open the domain, Email, Email Routing, Routing rules, Create address: hello, Send to a Worker, {name}.")


def cmd_deploy(a):
    cfg_path, cfg = load_config(a.slug)
    refresh_listings(a.slug)
    wrangler(["deploy"], worker_dir(a.slug), wrangler_env(cfg["name"], cfg.get("account_id")), quiet=True)
    print(f"deployed {cfg['name']} with the current listings")


def cmd_wire_form(a):
    cfg_path, cfg = load_config(a.slug)
    url = cfg["vars"].get("WORKER_URL")
    if not url:
        sys.exit("the worker has no WORKER_URL yet; run setup first")
    sj = os.path.join(site_dir(a.slug), "src", "data", "site.json")
    site = json.load(open(sj, encoding="utf-8"))
    site.setdefault("contact", {})["formEndpoint"] = f"{url}/claim"
    with open(sj, "w", encoding="utf-8") as fh:
        json.dump(site, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"site.json contact.formEndpoint is now {url}/claim. Run Gate 5 (build) and deploy the site; then delete the old form at the form service.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("keys", "check", "deploy", "wire-form"):
        s = sub.add_parser(c); s.add_argument("--slug", required=True)
    s = sub.add_parser("save-key"); s.add_argument("which", choices=["anthropic", "cloudflare"]); s.add_argument("--slug", required=True)
    s = sub.add_parser("setup"); s.add_argument("--slug", required=True); s.add_argument("--review-to", required=True)
    s.add_argument("--name"); s.add_argument("--account-id"); s.add_argument("--forward-to")
    a = ap.parse_args()
    {"keys": cmd_keys, "save-key": cmd_save_key, "check": cmd_check, "setup": cmd_setup, "deploy": cmd_deploy, "wire-form": cmd_wire_form}[a.cmd](a)


if __name__ == "__main__":
    main()
