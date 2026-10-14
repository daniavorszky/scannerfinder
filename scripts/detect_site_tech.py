#!/usr/bin/env python3
"""Detect marketing / site technology from each practitioner's homepage HTML (free, no API).

Why not DataForSEO Technologies: on a 5-domain test it knew only 2 practitioner sites and reports no ad pixels.

Input:  data/listings_profiled.csv (url column)
Cache:  data/site_tech_cache.jsonl  (per url: detected signatures; resumable)
Output: data/listings_profiled.csv, adding:
  ad_pixels      Meta Pixel / Google Ads / TikTok / Pinterest / LinkedIn / Microsoft Ads / Snapchat
  analytics      Google Analytics / GTM / Hotjar / Microsoft Clarity
  site_builder   WordPress / Wix / Squarespace / Shopify / GoDaddy / Weebly / Webflow / Duda / Showit / Kajabi / Carrd / Jimdo
  email_tool     Mailchimp / Klaviyo / Kit (ConvertKit) / ActiveCampaign / Flodesk / MailerLite / HubSpot / Keap
  chat_widget    Tawk / Intercom / Drift / Tidio / LiveChat / Crisp / Facebook chat / WhatsApp
  booking_widget booking scripts embedded on the homepage (complements booking_platform from links)
  pays_for_ads   yes when any ad pixel is present
Usage: python3 scripts/detect_site_tech.py [--workers 16]
"""
import argparse, csv, json, re, sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrich_site_details import fetch, PLATFORM  # same fetcher / platform filter as the site crawl

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")
CACHE = DATA / "site_tech_cache.jsonl"
SIGS = {
    "ad_pixels": {"Meta Pixel": r"connect\.facebook\.net/[^\"']*fbevents|fbq\(\s*['\"]init", "Google Ads": r"googleadservices|gtag\(\s*['\"]config['\"]\s*,\s*['\"]AW-|['\"]AW-\d{6,}",
                  "TikTok Pixel": r"analytics\.tiktok\.com|ttq\.load", "Pinterest Tag": r"s\.pinimg\.com/ct/|pintrk\(",
                  "LinkedIn Insight": r"snap\.licdn\.com|_linkedin_partner_id", "Microsoft Ads": r"bat\.bing\.com",
                  "Snapchat Pixel": r"sc-static\.net/scevent"},
    "analytics": {"Google Analytics": r"google-analytics\.com|gtag\(\s*['\"]config['\"]\s*,\s*['\"]G-|['\"]G-[A-Z0-9]{6,}['\"]|UA-\d{4,}-\d",
                  "Google Tag Manager": r"googletagmanager\.com/gtm|GTM-[A-Z0-9]{4,}", "Hotjar": r"static\.hotjar\.com|hjid",
                  "Microsoft Clarity": r"clarity\.ms"},
    "site_builder": {"WordPress": r"wp-content|wp-includes", "Wix": r"wix\.com|wixstatic|_wixCssImports", "Squarespace": r"squarespace",
                     "Shopify": r"cdn\.shopify|shopify\.com", "GoDaddy": r"godaddy|img1\.wsimg\.com", "Weebly": r"weebly",
                     "Webflow": r"webflow", "Duda": r"dudaone|multiscreensite|irp\.cdn-website", "Showit": r"showit",
                     "Kajabi": r"kajabi", "Carrd": r"carrd\.co", "Jimdo": r"jimdo", "Site123": r"site123", "Strikingly": r"strikingly"},
    "email_tool": {"Mailchimp": r"mailchimp|list-manage\.com|chimpstatic", "Klaviyo": r"klaviyo", "Kit (ConvertKit)": r"convertkit|kit\.com/forms",
                   "ActiveCampaign": r"activecampaign|activehosted", "Flodesk": r"flodesk", "MailerLite": r"mailerlite",
                   "HubSpot": r"hs-scripts|hsforms|hubspot", "Keap": r"infusionsoft|keap\.app"},
    "chat_widget": {"Tawk": r"tawk\.to", "Intercom": r"intercom", "Drift": r"drift\.com|js\.driftt", "Tidio": r"tidio",
                    "LiveChat": r"livechatinc", "Crisp": r"crisp\.chat", "Facebook chat": r"xfbml\.customerchat",
                    "WhatsApp": r"wa\.me/|api\.whatsapp\.com"},
    "booking_widget": {"Calendly": r"calendly", "Acuity": r"acuityscheduling|\.as\.me", "Square": r"squareup\.com/appointments|square\.site",
                       "Jane": r"janeapp", "Practice Better": r"practicebetter", "Cliniko": r"cliniko", "Vagaro": r"vagaro",
                       "Setmore": r"setmore", "Mindbody": r"mindbody|healcode", "Fresha": r"fresha", "SimplePractice": r"simplepractice"},
}


def detect(url):
    if not url or PLATFORM.search(url):
        return {"status": "skip"}
    for v in (url, url.replace("http://", "https://")):
        for ua in range(2):
            try:
                _, html = fetch(v, ua=ua)
                if html:
                    return {"status": "ok", **{k: [n for n, rx in s.items() if re.search(rx, html, re.I)] for k, s in SIGS.items()}}
            except Exception:
                continue
    return {"status": "unreachable"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=16); args = ap.parse_args()
    rows = list(csv.DictReader(open(DATA / "listings_profiled.csv")))
    cache = {}
    if CACHE.exists():
        for line in open(CACHE):
            o = json.loads(line); cache[o["url"]] = o["res"]
    todo = sorted({r["url"] for r in rows if r["url"] and r["site_crawl_status"] == "ok" and r["url"] not in cache})
    print(f"{len(todo)} homepages to scan ({len(cache)} cached)", flush=True)
    with open(CACHE, "a") as cf, ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(detect, u): u for u in todo}
        for i, f in enumerate(as_completed(futs), 1):
            u = futs[f]
            try: res = f.result()
            except Exception as e: res = {"status": f"error:{type(e).__name__}"}
            cache[u] = res; cf.write(json.dumps({"url": u, "res": res}) + "\n"); cf.flush()
            if i % 100 == 0 or i == len(todo): print(f"  {i}/{len(todo)}", flush=True)
    for r in rows:
        res = cache.get(r["url"], {})
        for k in SIGS:
            r[k] = "; ".join(res.get(k, []))
        r["pays_for_ads"] = "yes" if r["ad_pixels"] else ""
    with open(DATA / "listings_profiled.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    from collections import Counter
    live = [r for r in rows if r["status"] == "include" and cache.get(r["url"], {}).get("status") == "ok"]
    print(f"scanned ok: {len(live)}")
    for k in list(SIGS) + ["pays_for_ads"]:
        c = Counter(x for r in live for x in r[k].split("; ") if x)
        print(f"{k}: {sum(1 for r in live if r[k])} | {c.most_common(8)}")


if __name__ == "__main__":
    main()
