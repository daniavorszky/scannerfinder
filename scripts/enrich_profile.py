#!/usr/bin/env python3
"""Add profiling fields from the cached website text (no crawling, no AI, free).

Input:  data/listings_enriched.csv + data/site_text_cache.jsonl (written by enrich_site_details.py)
Output: data/listings_profiled.csv adds:
  device_models       models named on the site, only for brands already detected (e.g. "ZYTO Elite; BICOM optima")
  practitioner_type   main type: naturopath / chiropractor / nutrition / homeopath / acupuncture / kinesiology /
                      massage-bodywork / health coach / functional medicine / energy-holistic (fallback from Google category)
  credentials         post-nominals found (ND, DC, CNHP, LAc, FNTP, NTP, CCH, HHP...)
  booking_platform    Calendly, Jane, Acuity, Square, Practice Better, Cliniko... (from outbound links)
  supplement_brands   practitioner-channel / retail supplement brands named on the site
  mlm_signal          MLM companies or distributor wording (Solex, doTERRA, Young Living, Zinzino, Healy, iTOVi...)
  free_consult        yes + snippet
  animal_scanning     yes + snippet
  packages            largest session package found ("4-session package")
  profile_evidence    short snippets for the yes/no fields
Session prices are extracted separately by AI (scripts/merge_prices.py) - regex could not tell scan prices from other services.
Usage: python3 scripts/enrich_profile.py
"""
import csv, json, re
import os
from collections import Counter
from pathlib import Path

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")

MODELS = {  # brand family (as in devices_all) -> [(label, regex)]
    "ZYTO": [("ZYTO Elite", r"zyto elite"), ("ZYTO Balance", r"zyto balance"), ("ZYTO Select", r"zyto select"),
             ("ZYTO Evox", r"\bevox\b"), ("ZYTO Hand Cradle", r"hand cradle"), ("ZYTO Insight", r"zyto insight")],
    "BICOM": [("BICOM optima", r"\boptima\b"), ("BICOM 2000", r"bicom 2000"), ("BICOM MultiCom", r"multicom")],
    "Asyra/Qest4": [("Asyra Pro", r"asyra pro"), ("QEST4", r"\bqest ?4\b")],
    "NES Health": [("NES miHealth", r"mihealth"), ("NES ProVision", r"nes provision|provision scan")],
    "Rayonex": [("Rayocomp PS 1000", r"ps ?1000"), ("Rayocomp PS 10", r"ps ?10\b")],
    "NLS": [("Hunter 4025", r"hunter ?4025"), ("Oberon", r"\boberon\b"), ("Metatron", r"\bmetatron\b"),
            ("Sensitiv Imago", r"sensitiv imago")],
    "SCIO/Indigo/Eductor": [("SCIO", r"\bscio\b"), ("Indigo", r"\bindigo\b"), ("Eductor", r"\beductor\b"),
                            ("QUEST S", r"\bquest s\b"), ("QXCI", r"\bqxci\b")],
    "MORA": [("MORA Nova", r"mora nova"), ("MORA Super", r"mora super")],
    "TimeWaver": [("TimeWaver Pro", r"timewaver pro"), ("TimeWaver Mobile", r"timewaver mobile"),
                  ("TimeWaver Frequency", r"timewaver frequency"), ("TimeWaver Home", r"timewaver home")],
}
# (type, regex) in priority order; first hit wins for practitioner_type, all hits kept in types_all
TYPES = [
    ("naturopath", r"naturopath"), ("chiropractor", r"chiropract"), ("functional medicine", r"functional medicine"),
    ("acupuncture", r"acupunctur|chinese medicine"), ("homeopath", r"homeopath|homoeopath"),
    ("nutrition", r"nutritionist|nutritional therap|dietitian|clinical nutrition"),
    ("kinesiology", r"kinesiolog"), ("osteopath", r"osteopath"), ("herbalist", r"herbalist|naturopathic herbal"),
    ("massage-bodywork", r"massage therap|reflexolog|bodywork"), ("health coach", r"health coach|wellness coach"),
    # DE + RO (2026-10-12); after the English types so mixed-language sites keep their English hit
    ("physician", r"\bdr\. ?med\.(?! ?vet)|fachärzt|facharzt|allgemeinmedizin|\bmedic (?:primar|specialist)|medic de familie"),
    ("dentist", r"zahnarzt|zahnärzt|zahnmedizin|medic stomatolog|stomatologie"),
    ("naturopath", r"heilprakti|naturheilpraxis|naturheilkunde|naturopat|terapeut naturist"),
    ("homeopath", r"homöopath|homoeopath|homeopat"), ("acupuncture", r"akupunktur|acupunctur|\btcm\b"),
    ("kinesiology", r"kinesiolog"), ("osteopath", r"osteopathie|osteopat"),
    ("nutrition", r"ernährungsberat|ernährungsthera|nutriționist|nutritionist|nutriţionist|dietetician"),
    ("massage-bodywork", r"fußreflex|massagepraxis|masaj"), ("health coach", r"gesundheitscoach|coach de sănătate"),
]
CATEGORY_TYPES = [("physician", r"doctor|physician|urolog|dermatolog|pediatric|gynecolog|otolaryng|internist|orthopedic"),
                  ("dentist", r"dentist"), ("naturopath", r"heilprakt"), ("chiropractor", r"chiropract"), ("naturopath", r"naturopath"), ("acupuncture", r"acupunct"),
                  ("homeopath", r"homeopath"), ("nutrition", r"nutrition|dietitian"), ("massage-bodywork", r"massage|reflexolog"),
                  ("kinesiology", r"kinesiolog"), ("energy-holistic", r"holistic|alternative|wellness|reiki|energy|healing|medicine")]
# post-nominals: case-sensitive, must follow a comma/name or stand alone in caps
CRED_RX = re.compile(r"(?<![A-Za-z])(N\.D\.|ND|D\.C\.|DC|CNHP|L\.Ac\.?|LAc|FNTP|NTP|CCH|HHP|CNC|DNM|BHSc|MNIMH|RHom|IFMCP)(?![A-Za-z])")
# DE/RO titles are words, not post-nominals: matched anywhere, case-insensitive
CRED_WORDS = {"Heilpraktiker": r"\bheilpraktiker(?:in)?\b", "Dr. med.": r"\bdr\. ?med\.(?! ?vet| ?dent)",
              "Dr. med. dent.": r"\bdr\. ?med\. ?dent\.", "Facharzt": r"\bfachärzt(?:in)?\b|\bfacharzt\b",
              "Medic primar": r"\bmedic primar\b", "Medic specialist": r"\bmedic specialist\b"}
CRED_CONTEXT = re.compile(r"[A-Z][a-z]+,? ?$")  # preceded by a capitalised name, e.g. "Jane Smith, ND"
BOOKING = {"calendly": "Calendly", "janeapp": "Jane", "jane.app": "Jane", "acuityscheduling": "Acuity", "as.me": "Acuity",
           "squareup": "Square", "square.site": "Square", "practicebetter": "Practice Better", "cliniko": "Cliniko",
           "vagaro": "Vagaro", "setmore": "Setmore", "gettimely": "Timely", "fresha": "Fresha", "10to8": "10to8",
           "mindbodyonline": "Mindbody", "wellnessliving": "WellnessLiving", "bookwhen": "Bookwhen", "zocdoc": "Zocdoc",
           "simplepractice": "SimplePractice", "schedulista": "Schedulista", "halaxy": "Halaxy", "nookal": "Nookal",
           "youcanbook": "YouCanBookMe", "timetap": "TimeTap", "genbook": "Genbook", "booksy": "Booksy",
           "doctolib": "Doctolib", "terminland": "Terminland", "etermin": "eTermin", "samedi": "samedi",
           "jameda": "jameda", "simplybook": "SimplyBook.me", "termin-direkt": "Termin-direkt", "docplanner": "Docplanner"}
SUPPLEMENTS = {"Standard Process": r"standard process", "Metagenics": r"metagenics", "Designs for Health": r"designs for health",
               "Pure Encapsulations": r"pure encapsulations", "Thorne": r"\bthorne\b", "Biotics Research": r"biotics research",
               "Apex Energetics": r"apex energetics", "Deseret Biologicals": r"desbio|deseret biologicals",
               "Energetix": r"\benergetix\b", "Heel": r"\bheel (?:inc|homeopathic|remed|product)|\bheel gmbh",
               "Orthomolecular": r"orthomolecular products", "Quicksilver": r"quicksilver scientific", "CellCore": r"cellcore",
               "Guna": r"\bguna\b", "Seroyal": r"seroyal", "Douglas Labs": r"douglas lab", "Systemic Formulas": r"systemic formulas",
               "Natural Factors": r"natural factors", "doTERRA": r"doterra", "Young Living": r"young living",
               "Shaklee": r"shaklee", "USANA": r"\busana\b", "Isagenix": r"isagenix", "Arbonne": r"arbonne", "Zinzino": r"zinzino"}
MLM = {"Solex (AO Scan)": r"\bsolex\b", "doTERRA": r"doterra", "Young Living": r"young living", "Zinzino": r"zinzino",
       "Healy World": r"\bhealy\b", "iTOVi": r"\bitovi\b", "Arbonne": r"arbonne", "Isagenix": r"isagenix", "USANA": r"\busana\b",
       "Forever Living": r"forever living", "distributor wording": r"independent distributor|wellness advocate|brand partner|"
       r"become a distributor|join my team|business opportunity"}
FREE_RX = re.compile(r"free (?:consult\w*|discovery\w*|1[05]|20|30|initial|intro\w*|scan|call|phone)|complimentary (?:consult\w*|scan|call|discovery)"
                     r"|kostenlose[sn]? (?:erstgespräch|vorgespräch|beratung|kennenlern\w*)|unverbindliche[sn]? (?:erstgespräch|vorgespräch)"
                     r"|consulta(?:ț|t|ţ)ie gratuit\w*|prima (?:consulta(?:ț|t|ţ)ie|evaluare) gratuit\w*|evaluare gratuit\w*", re.I)
PET_RX = re.compile(r"\b(?:scan\w*|bioresonance|biofeedback|sessions?|zyto|treatments?|therapy|testing)\b(?: is| are)?(?: also)?(?: available)?"
                    r" (?:for|on) (?:your |our |their )?(?:pets?|dogs?|cats?|horses?|animals?)\b|"
                    r"\bpet (?:scan|session|bioresonance|biofeedback)s?\b|\b(?:equine|canine|veterinary) (?:scan|bioresonance|biofeedback|session|therapy)|"
                    r"\b(?:bioresonance|biofeedback|scans?) for (?:pets|animals|horses|dogs)\b|\bwork on animals\b|\b(?:performed|done|used) on (?:your )?(?:pets|animals)\b|"
                    r"\bfür (?:mensch und tier|tiere|hunde|pferde|katzen)\b|\btierheilprakti|\bbioresonanz (?:für|bei) tier|"
                    r"\bpentru animale\b|\bși animale(?:lor)?\b", re.I)
PET_FALSE = re.compile(r"cat scan|lead dog|virus scan|pet allerg|allergy to|dog walk|MRI|CT scan|CT &|as well as humans|magnet", re.I)
PKG_RX = re.compile(r"\b(?:package|bundle|course|block) of (\d{1,2})\b|\b(\d{1,2})[- ]?(?:session|treatment|visit)s? (?:package|bundle|pack|block)\b"
                    r"|\b(\d{1,2})er[- ](?:karte|paket|abo)\b|\bpachet (?:de )?(\d{1,2}) ședințe\b", re.I)



def snip(t, m, w=60):
    return t[max(0, m.start() - w): m.end() + w].strip()


def profile(row, res):
    text, ext = res.get("text", ""), res.get("ext_links", "")
    low = text.lower()
    fams = [d for d in row["devices_all"].split("; ") if d]
    out, ev = {}, []

    models = []
    for fam in fams:
        for label, rx in MODELS.get(fam, []):
            if re.search(rx, low):
                models.append(label)
    out["device_models"] = "; ".join(dict.fromkeys(models))

    types = [t for t, rx in TYPES if re.search(rx, low)]
    creds = []
    for m in CRED_RX.finditer(text):
        before = text[max(0, m.start() - 25): m.start()]
        if CRED_CONTEXT.search(before):
            c = m.group(1).replace(".", "")
            if c not in creds:
                creds.append(c)
    for label, rx in CRED_WORDS.items():
        if re.search(rx, text[:60000], re.I) and label not in creds:
            creds.append(label)
    if "ND" in creds and "naturopath" not in types: types.insert(0, "naturopath")
    if "DC" in creds and "chiropractor" not in types: types.insert(0, "chiropractor")
    if not types:
        cat = (row.get("category") or "").lower()
        types = [t for t, rx in CATEGORY_TYPES if re.search(rx, cat)][:1] or (["energy-holistic"] if text else [])
    out["practitioner_type"] = types[0] if types else ""
    out["practitioner_types_all"] = "; ".join(types)
    out["credentials"] = "; ".join(creds)

    out["booking_platform"] = "; ".join(dict.fromkeys(v for k, v in BOOKING.items() if k in ext.lower()))
    out["supplement_brands"] = "; ".join(k for k, rx in SUPPLEMENTS.items() if re.search(rx, low))
    out["mlm_signal"] = "; ".join(k for k, rx in MLM.items() if re.search(rx, low))
    if "AO Scan" in fams and "Solex (AO Scan)" not in out["mlm_signal"]:
        out["mlm_signal"] = "; ".join(filter(None, [out["mlm_signal"], "Solex (AO Scan)"]))

    m = FREE_RX.search(text)
    out["free_consult"] = "yes" if m else ""
    if m: ev.append("free: " + snip(text, m, 40))
    pet = next((p for p in PET_RX.finditer(text) if not PET_FALSE.search(snip(text, p, 15))), None)
    out["animal_scanning"] = "yes" if pet else ""
    if pet: ev.append("animals: " + snip(text, pet, 30))
    sizes = sorted({int(next(g for g in m if g)) for m in PKG_RX.findall(text) if 2 <= int(next(g for g in m if g)) <= 24})
    out["packages"] = f"{sizes[-1]}-session package" if sizes else ""
    out["profile_evidence"] = " | ".join(ev)[:500]
    return out


def main():
    rows = list(csv.DictReader(open(DATA / "listings_enriched.csv")))
    cache = {}
    for line in open(DATA / "site_text_cache.jsonl"):
        o = json.loads(line); cache[o["url"]] = o["res"]
    out = [{**r, **profile(r, cache.get(r["url"], {}))} for r in rows]
    with open(DATA / "listings_profiled.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

    n = len(out)
    for k in ("device_models", "practitioner_type", "credentials", "booking_platform", "supplement_brands",
              "mlm_signal", "free_consult", "animal_scanning", "packages"):
        filled = [o[k] for o in out if o[k]]
        c = Counter(x for v in filled for x in v.split("; "))
        print(f"{k}: {len(filled)}/{n} | {c.most_common(8)}")


if __name__ == "__main__":
    main()
