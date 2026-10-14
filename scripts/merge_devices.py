#!/usr/bin/env python3
"""Merge AI device identification (listings where the keyword search found no device) into the profiled listings.

Input:  data/listings_profiled.csv + data/device_batches/out_*.jsonl
        (AI read Google description + website snippets from data/device_batches/batch_*.jsonl)
Output: data/listings_profiled.csv, adding:
  offers_scanning   yes / no / unclear (AI; blank where a device was already known from keywords)
  service_kind      bioresonance therapy / biofeedback / intolerance-allergy testing / health-wellness scan / frequency therapy / other
  device_other      named device outside the brand list (e.g. Monicor, Ondamed, Harmonic Egg)
  device_ai_confidence, device_ai_evidence
  devices_all       extended with the AI brand when it is one of the known families
Pipeline order: enrich_profile.py -> merge_prices.py -> detect_site_tech.py -> merge_devices.py
Usage: python3 scripts/merge_devices.py
"""
import csv, json
import os
from collections import Counter
from pathlib import Path

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")
NOT_A_BRAND = {None, "", "Other", "Hair/remote test (no device named)"}


def main():
    ai = {}
    for f in sorted((DATA / "device_batches").glob("out_*.jsonl")):
        for line in open(f):
            if line.strip():
                o = json.loads(line); ai[str(o["cid"])] = o
    rows = list(csv.DictReader(open(DATA / "listings_profiled.csv")))
    for r in rows:
        o = ai.get(r["cid"])
        r.setdefault("device_other", "")
        if not o:
            for k in ("offers_scanning", "service_kind", "device_other", "device_ai_confidence", "device_ai_evidence"):
                r[k] = r.get(k, "")
            continue
        brand = o.get("device_brand")
        if brand not in NOT_A_BRAND and brand not in r["devices_all"].split("; "):
            r["devices_all"] = "; ".join(filter(None, [r["devices_all"], brand]))
        if brand == "Hair/remote test (no device named)":
            o["service_kind"] = o.get("service_kind") or "intolerance/allergy testing"
        r["offers_scanning"] = o.get("offers_scanning") or ""
        r["service_kind"] = o.get("service_kind") or ""
        r["device_other"] = o.get("device_other") or ("hair/remote test" if brand == "Hair/remote test (no device named)" else "")
        if o.get("device_model") and o["device_model"] not in r["device_models"]:
            r["device_models"] = "; ".join(filter(None, [r["device_models"], o["device_model"]]))
        r["device_ai_confidence"] = o.get("confidence") or ""
        r["device_ai_evidence"] = (o.get("evidence") or "")[:160]
        if r["offers_scanning"] == "no" and r["status"] == "include":
            r["status"], r["reason"] = "review", "AI found no device-based scanning service (2026-10-12)"
    with open(DATA / "listings_profiled.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    inc = [r for r in rows if r["status"] == "include"]
    print(f"AI rows {len(ai)} | matched {sum(r['cid'] in ai for r in rows)} | status: {Counter(r['status'] for r in rows)}")
    print("offers_scanning:", Counter(ai[c].get('offers_scanning') for c in ai).most_common())
    print("AI brands:", Counter(o.get('device_brand') for o in ai.values()).most_common(12))
    print("service_kind:", Counter(o.get('service_kind') for o in ai.values()).most_common())
    print(f"include with known device family: {sum(1 for r in inc if r['devices_all'])}/{len(inc)}"
          f" | + named other device: {sum(1 for r in inc if not r['devices_all'] and r['device_other'])}")


if __name__ == "__main__":
    main()
