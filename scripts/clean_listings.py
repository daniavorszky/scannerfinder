#!/usr/bin/env python3
"""Classify data/listings_flat.csv into include / review / exclude for the ScannerFinder directory.

Rule of thumb: a listing is in if its own text proves it offers a scan with an in-scope device
(or bioresonance as a category) AND it is a practitioner, not a manufacturer/distributor or unrelated business.

Output: data/listings_classified.csv (all rows + status, reason, devices, flags)
        data/listings_include.csv, data/listings_review.csv
"""
import csv, re
import os
from collections import Counter
from pathlib import Path

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")

# Device evidence: device name in a context that clearly means the scanner, not a town/charity/solar firm.
DEVICES = {
    "ZYTO":        r"\bzyto\b",
    "BICOM":       r"\bbicom\b",
    "Asyra/Qest4": r"\basyra\b|\bqest ?4\b",
    "NES Health":  r"\bnes (health|scan|bioenergetic|miHealth)|\bbioenergetix\b|\bnes\b.{0,20}\bbody ?field",
    "Rayonex":     r"\brayonex\b|\brayocomp\b",
    "NLS":         r"\bnls\b|\bhunter ?4025\b|\bmetatron\b.{0,40}(nls|hunter|4025|scan|system|bio-?resonance|device|machine|analys)"
                   r"|(nls|scan|bio-?resonance|device|machine)\b.{0,40}\bmetatron\b|\boberon\b.{0,30}(nls|scan|bio|device|analys)",
    "SCIO/Indigo/Eductor": r"\bscio\b.{0,30}(biofeedback|device|scan|session|quantum)|(biofeedback|quantum)\b.{0,30}\bscio\b"
                   r"|\beductor\b|\bindigo\b.{0,20}biofeedback|\bquantum biofeedback\b|\bqxci\b",
    "MORA":        r"\bmora\b.{0,20}(therapy|bio-?resonance|device|super|nova)",
    "TimeWaver":   r"\btimewaver\b",
    "AO Scan":     r"\bao ?scan\b|\bsolex\b.{0,40}(scan|frequenc|wellness|vitals)",
}
CATEGORY_EVIDENCE = r"bio[- ]?r[ée]sonan|biofeedback scan|bio[- ]?resonanz|bio[- ]?communi[ck]ation|bio[- ]?rezonan"
EXCLUDED_DEVICES = r"\bhealy\b|\bitovi\b|quantum resonance magnetic"
MLM = r"do ?terra|young living|independent (distributor|consultant)|\bdistributor\b|\bmlm\b|solex (partner|affiliate)"
MANUFACTURER_TITLE = r"^zyto\b|rayonex|regumed|timewaver|asyra ltd|nes health|energy4life|^solex\b|metatron (australia|uk|usa)|bicom (uk|usa|australia)"

HEALTH_CATEGORY = re.compile(
    r"health|wellness|holistic|naturopath|chiropract|nutrition|biofeedback|therap|clinic|acupunct|homeopath|"
    r"healing|healer|massage|integrative|medicine|medical|kinesiolog|reiki|reflexolog|herbal|doctor|physician|"
    r"counsel|coach|spa\b|osteopath|physio|dietitian|hypno|psych|weight loss|detox|colonic|ayurved|chinese medicine|"
    r"skin care|beauty|salon|yoga|pilates|fitness|alternative|energy|practitioner|centre|center|heilprakt|naturheil", re.I)
NOISE_CATEGORY = re.compile(
    r"solar|construction|council|dance|charity|coffee|cafe|restaurant|school|auto|car |real estate|builder|"
    r"manufacturer|corporate office|wholesaler|laboratory|church|hotel|bar\b|pub\b|software|computer|engineer|"
    r"plumb|electric|insurance|bank|lawyer|attorney|accountant|association|organization|non-profit|government|"
    r"museum|park|store|shop|supplier", re.I)


def classify(r):
    title, desc, cat = r["title"] or "", r["description"] or "", r["category"] or ""
    text = f"{title} {desc}".lower()
    devices = [name for name, rx in DEVICES.items() if re.search(rx, text, re.I)]
    cat_ev = bool(re.search(CATEGORY_EVIDENCE, text, re.I))
    flags = []
    if re.search(MLM, text, re.I):
        flags.append("mlm/distributor-mention")
    if re.search(EXCLUDED_DEVICES, text, re.I):
        flags.append("excluded-device-mention")
    if not r["emails"]:
        flags.append("no-email")

    if re.search(MANUFACTURER_TITLE, title, re.I) or re.search(r"manufacturer|wholesaler|corporate office", cat, re.I):
        return "exclude", "manufacturer/distributor", devices, flags
    if not devices and not cat_ev and re.search(r"biofeedback|bio-?energetic scan|frequency scan", text, re.I) \
            and HEALTH_CATEGORY.search(cat):
        return "review", "generic biofeedback/scan, device unknown", devices, flags
    if not devices and not cat_ev:
        return "exclude", "no device/bioresonance evidence in own text", devices, flags
    if NOISE_CATEGORY.search(cat) and not HEALTH_CATEGORY.search(cat):
        return "review", f"evidence ok but non-practitioner category: {cat}", devices, flags
    if not cat:
        return "review", "no category", devices, flags
    if not HEALTH_CATEGORY.search(cat):
        return "review", f"unusual category: {cat}", devices, flags
    if "excluded-device-mention" in flags and not devices:
        return "review", "bioresonance + excluded consumer device (Healy/iTOVi)", devices, flags
    return "include", "device evidence" if devices else "bioresonance category", devices, flags


def main():
    rows = list(csv.DictReader(open(DATA / "listings_flat.csv")))
    manual = {}
    if (DATA / "manual_review.csv").exists():
        manual = {m["cid"]: m["decision"] for m in csv.DictReader(open(DATA / "manual_review.csv"))}
    out = []
    for r in rows:
        status, reason, devices, flags = classify(r)
        if r["cid"] in manual:
            status, reason = manual[r["cid"]], f"manual review (Dan): {reason}"
        out.append({"status": status, "reason": reason, "devices": "; ".join(devices),
                    "flags": "; ".join(flags), **r})
    fields = list(out[0].keys())
    for name, subset in (("listings_classified.csv", out),
                         ("listings_include.csv", [o for o in out if o["status"] == "include"]),
                         ("listings_review.csv", [o for o in out if o["status"] == "review"])):
        with open(DATA / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(subset)
    print(Counter(o["status"] for o in out))
    print(Counter((o["country"], o["status"]) for o in out))


if __name__ == "__main__":
    main()
