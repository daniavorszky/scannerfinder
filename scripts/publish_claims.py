#!/usr/bin/env python3
"""Publish approved ScannerFinder claims to the site (plan: research/claim-flow-plan.md, rule A, 2026-10-14).

Reads every claim and its latest profile from D1, approves what rule A allows, writes the publishable
fields to site/src/data/claims-overlay.json, and prints what still waits for Dan. Then build + deploy.

Usage:
  python3 scripts/publish_claims.py [--dry-run] [--approve ID ...] [--reject ID ...] [--drop-description ID ...]
                                    [--out PATH] [--local PERSIST_DIR]

Rule A (Dan, 2026-10-14): approved automatically when ownership is confirmed (status `verified`, i.e. the
email is one we found on the practice's site or sits on its domain) and the description passes
wellness_lint. Manual-ownership claims (status `email_confirmed`: Dan calls the Google number first) and
lint failures wait for --approve. New practices (no listing) are reported, never added automatically.
Session prices reach the overlay only when the practitioner chose to show them (price_public).
"""
import argparse, json, os, re, subprocess, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from wellness_lint import BANNED, PRICE  # noqa: E402  (one canonical rule set for every text on the site)

SITE = os.path.join(os.path.dirname(HERE), "apps", "directory-blueprint", "output", "scannerfinder", "site")
UUID = re.compile(r"^[0-9a-f-]{36}$")


def d1(sql, args):
    where = ["--local", "--persist-to", args.local] if args.local else ["--remote"]
    r = subprocess.run(["npx", "wrangler", "d1", "execute", "scannerfinder", *where, "--json", "--command", sql],
                       cwd=SITE, capture_output=True, text=True, env={**os.environ, "CI": "1"})
    if r.returncode != 0:
        sys.exit(f"wrangler failed:\n{r.stderr[-1500:]}")
    return json.loads(r.stdout)[-1]["results"]


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def lint(text):
    return sorted({m.group(0).lower() for m in BANNED.finditer(text or "")} | {m.group(0) for m in PRICE.finditer(text or "")})


def overlay_entry(data, reviewed_at):
    price = None
    if data.get("price_public") and data.get("session_price"):
        price = {"currency": data.get("currency"), "first": data["session_price"], "followup": data.get("followup_price")}
    e = {
        "business_name": data.get("business_name") or None, "phone": data.get("phone") or None,
        "website": data.get("website") or None, "booking_url": data.get("booking_url") or None,
        "devices": data.get("devices") or [], "device_models": data.get("device_models") or None,
        "remote_sessions": data.get("remote_sessions"), "free_consultation": data.get("free_consultation"),
        "description": data.get("description") or None, "session_minutes": data.get("session_minutes"),
        "package_note": data.get("package_note") or None,
        "price": price, "price_confirmed": bool(data.get("session_price")),
        "approved_on": (reviewed_at or "")[:10],
    }
    return {k: v for k, v in e.items() if v not in (None, "", [])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--approve", nargs="*", default=[])
    ap.add_argument("--reject", nargs="*", default=[])
    ap.add_argument("--drop-description", nargs="*", default=[])
    ap.add_argument("--out", default=os.path.join(SITE, "src", "data", "claims-overlay.json"))
    ap.add_argument("--local", help="wrangler --persist-to folder: read a local D1 instead of production")
    args = ap.parse_args()
    for i in args.approve + args.reject + args.drop_description:
        if not UUID.match(i):
            sys.exit(f"not a claim id: {i}")

    rows = d1("""SELECT c.id, c.listing_slug, c.status, c.verify_method, c.name, c.email, c.details,
                        p.version, p.data, p.reviewed_at
                 FROM claims c JOIN profile_public p ON p.claim_id = c.id
                 ORDER BY c.id, p.version""", args)
    claim_data = json.load(open(os.path.join(SITE, "functions", "_data", "claim-data.json")))
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    by_claim = {}
    for r in rows:
        by_claim.setdefault(r["id"], []).append(r)

    overlay, writes = {}, []
    approved_now, waiting, held, new_practices, rejected = [], [], [], [], []
    for cid, versions in by_claim.items():
        latest = versions[-1]
        slug, status = latest["listing_slug"], latest["status"]
        data = json.loads(latest["data"])
        label = (claim_data.get(slug) or {}).get("n") or data.get("business_name") or slug
        if cid in args.reject:
            writes.append(f"UPDATE claims SET status = 'rejected', updated_at = {q(now)} WHERE id = {q(cid)}")
            rejected.append(label)
            continue
        if status == "rejected":
            continue
        if not slug:
            new_practices.append((cid, data.get("business_name"), json.loads(latest["details"] or "{}").get("new_practice"), latest["email"]))
            continue
        if cid in args.drop_description and data.get("description"):
            data["description"] = ""
            writes.append(f"UPDATE profile_public SET data = {q(json.dumps(data))} WHERE claim_id = {q(cid)} AND version = {latest['version']}")
        problems = lint(data.get("description"))
        owner_ok = status in ("verified", "approved") or cid in args.approve
        if owner_ok and not problems:
            reviewed = latest["reviewed_at"] or now
            if not latest["reviewed_at"]:
                writes.append(f"UPDATE profile_public SET reviewed_at = {q(now)} WHERE claim_id = {q(cid)} AND version = {latest['version']}")
                approved_now.append(f"{label} (v{latest['version']}, {latest['verify_method'] if cid not in args.approve else 'approved by Dan'})")
            if status != "approved":
                writes.append(f"UPDATE claims SET status = 'approved', updated_at = {q(now)} WHERE id = {q(cid)}")
            overlay[slug] = overlay_entry(data, reviewed)
            continue
        if problems:
            held.append((cid, label, problems))
        else:
            ph = (claim_data.get(slug) or {}).get("ph", "")
            waiting.append((cid, label, latest["name"], latest["email"], ph))
        # Until the new version passes, the last approved one stays on the site.
        prev = [v for v in versions if v["reviewed_at"]]
        if prev:
            overlay[slug] = overlay_entry(json.loads(prev[-1]["data"]), prev[-1]["reviewed_at"])

    if writes and not args.dry_run:
        d1("; ".join(writes), args)
    if not args.dry_run:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(overlay.items())), f, ensure_ascii=False, indent=1)

    tag = " (dry run: nothing written)" if args.dry_run else ""
    print(f"Published listings: {len(overlay)}{tag} -> {os.path.relpath(args.out)}")
    for a in approved_now:
        print(f"  approved now: {a}")
    for r in rejected:
        print(f"  rejected: {r}")
    if waiting:
        print("\nWaiting for Dan (owner not confirmed: call the Google number, then --approve <id>):")
        for cid, label, name, email, ph in waiting:
            print(f"  {cid}  {label}  | {name} <{email}> | call {ph or 'no phone on file'}")
    if held:
        print("\nHeld (description fails wellness_lint: --drop-description <id> keeps our text, or ask them to rewrite):")
        for cid, label, problems in held:
            print(f"  {cid}  {label}  | {', '.join(problems)}")
    if new_practices:
        print("\nNew practices (not in the directory: add by hand, then they can be approved):")
        for cid, name, np, email in new_practices:
            print(f"  {cid}  {name} | {np} | {email}")
    if writes or (not args.dry_run and overlay):
        print("\nNext: build + deploy the site.")


if __name__ == "__main__":
    main()
