#!/usr/bin/env python3
"""Gate 5 (ScannerFinder): adds `region` + `region_slug` + `country_slug` to the site's listings.csv.

Runs AFTER the kit's apply_exclusions.py, on site/src/data/listings.csv (rewrites it in place).
Decision in 04-plan.md (2026-10-12): country → region → listing.
- US / CA / AU: region from DataForSEO, abbreviations normalized.
- GB: postcode area → ITL1 region (offline table below).
- ZA / NZ: city → province/region (table below).
- IE: county from DataForSEO or the city (all under the floor → listed on the country hub).
- No city/region: the nearest listing in the same country (by coordinates) gives the region.
"""
import csv, math, re, sys, unicodedata, os

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_CSV = os.path.join(os.path.dirname(HERE), "apps", "directory-blueprint", "output", "scannerfinder", "site", "src", "data", "listings.csv")

COUNTRY_SLUG = {"US": "united-states", "GB": "united-kingdom", "CA": "canada", "AU": "australia",
                "ZA": "south-africa", "IE": "ireland", "NZ": "new-zealand", "DE": "germany", "RO": "romania"}

US = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut",
      "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
      "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
      "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
      "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
      "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
      "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin",
      "WY": "Wyoming", "DC": "District of Columbia"}
CA = {"AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba", "NB": "New Brunswick", "NL": "Newfoundland and Labrador",
      "NS": "Nova Scotia", "ON": "Ontario", "PE": "Prince Edward Island", "QC": "Quebec", "SK": "Saskatchewan"}
AU = {"NSW": "New South Wales", "VIC": "Victoria", "QLD": "Queensland", "SA": "South Australia", "WA": "Western Australia",
      "TAS": "Tasmania", "ACT": "Australian Capital Territory", "NT": "Northern Territory"}

GB_AREAS = {
    "London": "E EC N NW SE SW W WC BR CR HA IG RM SM UB DA",
    "South East": "BN CT GU HP ME MK OX PO RG RH SL SO TN",
    "East of England": "AL CB CM CO IP LU NR PE SG SS WD",
    "South West": "BA BH BS DT EX GL PL SN SP TA TQ TR",
    "West Midlands": "B CV DY HR ST TF WR WS WV",
    "East Midlands": "DE LE LN NG NN",
    "Yorkshire and the Humber": "BD DN HD HG HU HX LS S WF YO",
    "North West": "BB BL CA CH CW FY L LA M OL PR SK WA WN",
    "North East": "DH DL NE SR TS",
    "Wales": "CF LD LL NP SA SY",
    "Scotland": "AB DD DG EH FK G HS IV KA KW KY ML PA PH TD ZE",
    "Northern Ireland": "BT",
}
GB = {a: reg for reg, s in GB_AREAS.items() for a in s.split()}
# Areas split between London and the neighbouring county, by district number.
GB_SPLIT = {"KT": (9, "London", "South East"), "TW": (14, "London", "South East"), "EN": (5, "London", "East of England")}

ZA = {"Western Cape": "Cape Town|George|Knysna|Melkbosstrand|Moorreesburg|Mossel Bay|Oudtshoorn|Pearl Valley Golf Estate and Spa|"
                      "Plettenberg Bay|Somerset West|St Helena Bay|Strand|Swellendam|Wilderness|Stellenbosch|Paarl",
      "Gauteng": "Alberton|Benoni|Boksburg|Centurion|Chartwell|Germiston|Johannesburg South|Johannesburg|Krugersdorp|Magaliesburg|"
                 "Meyerton|Midrand|Pretoria|Randburg|Sandton|Roodepoort",
      "KwaZulu-Natal": "Ballito|Durban|Gillitts|Hilton|Kloof|Margate|Pietermaritzburg|Umhlanga",
      "North West Province": "Mahikeng|Rustenburg", "Mpumalanga": "Mbombela|Middelburg|Volksrust", "Free State": "Parys"}
ZA = {c.lower(): p for p, s in ZA.items() for c in s.split("|")}
NZ = {"Auckland": "Auckland|Orewa|Pukekohe|Whangaparāoa|Whangaparaoa", "Canterbury": "Christchurch", "Gisborne": "Gisborne",
      "Wellington": "Lower Hutt|Wellington", "Nelson": "Nelson", "Bay of Plenty": "Rotorua|Tauranga"}
NZ = {c.lower(): p for p, s in NZ.items() for c in s.split("|")}

# Germany (added 2026-10-14): first two postcode digits → Land (English name where English has one, 04-plan DE/RO #3).
# Border prefixes (21, 37, 68, ...) are settled by DE_CITY first.
DE_PLZ = {}
for _land, _pfx in {
        "Saxony": "01 02 04 08 09", "Brandenburg": "03 14 15 16", "Saxony-Anhalt": "06 39", "Thuringia": "07 98 99",
        "Berlin": "10 12 13", "Mecklenburg-Vorpommern": "17 18 19", "Hamburg": "20 22", "Bremen": "28",
        "Lower Saxony": "21 26 27 29 30 31 37 38 49", "Schleswig-Holstein": "23 24 25",
        "North Rhine-Westphalia": "32 33 40 41 42 44 45 46 47 48 50 51 52 53 57 58 59",
        "Hesse": "34 35 36 60 61 63 64 65", "Rhineland-Palatinate": "54 55 56 67", "Saarland": "66",
        "Baden-Württemberg": "68 69 70 71 72 73 74 75 76 77 78 79 88 89",
        "Bavaria": "80 81 82 83 84 85 86 87 90 91 92 93 94 95 96 97"}.items():
    for _p in _pfx.split(): DE_PLZ[_p] = _land
# Towns in a prefix that mostly belongs to another Land (checked by hand on the 2026-10-14 data).
DE_CITY = {"bensheim": "Hesse", "heppenheim": "Hesse", "lampertheim": "Hesse", "viernheim": "Hesse", "lorsch": "Hesse",
           "neu-ulm": "Bavaria", "kassel": "Hesse", "witzenhausen": "Hesse", "eschwege": "Hesse", "heiligenstadt": "Thuringia",
           "geesthacht": "Schleswig-Holstein", "reinbek": "Schleswig-Holstein", "wentorf bei hamburg": "Schleswig-Holstein",
           "glinde": "Schleswig-Holstein", "norderstedt": "Schleswig-Holstein", "ahrensburg": "Schleswig-Holstein",
           "bad oldesloe": "Schleswig-Holstein", "aschaffenburg": "Bavaria", "alzenau": "Bavaria", "miltenberg": "Bavaria",
           "obernburg am main": "Bavaria", "wertheim": "Baden-Württemberg", "lindau": "Bavaria", "osnabrück": "Lower Saxony",
           "minden": "North Rhine-Westphalia", "bad oeynhausen": "North Rhine-Westphalia", "rahden": "North Rhine-Westphalia",
           "hille": "North Rhine-Westphalia", "petershagen": "North Rhine-Westphalia", "lübbecke": "North Rhine-Westphalia",
           "porta westfalica": "North Rhine-Westphalia", "vlotho": "North Rhine-Westphalia", "leipzig": "Saxony",
           "torgau": "Saxony", "altenburg": "Thuringia", "gera": "Thuringia", "hof": "Bavaria", "zwickau": "Saxony",
           # second pass on the 2026-10-14 data (prefixes 14, 17, 21, 29, 34, 36, 37, 63, 88, 89, 97)
           "berlin": "Berlin", "hamburg": "Hamburg", "lychen": "Brandenburg", "büchen": "Schleswig-Holstein",
           "hessisch lichtenau": "Hesse", "neu-eichenberg": "Hesse", "hann. münden": "Lower Saxony", "dermbach": "Thuringia",
           "bürgstadt": "Bavaria", "mömbris": "Bavaria", "salzwedel": "Saxony-Anhalt", "kammeltal": "Bavaria",
           "jettingen-scheppach": "Bavaria", "scheidegg": "Bavaria", "wertheim am main": "Baden-Württemberg",
           "trittau": "Schleswig-Holstein", "pirmasens": "Rhineland-Palatinate", "lemberg": "Rhineland-Palatinate",
           "riedelberg": "Rhineland-Palatinate", "lilienthal": "Lower Saxony", "wald-michelbach": "Hesse"}
# Romania: the first two postcode digits are the county (județ); English name only for Bucharest.
RO_PC = {"01": "Bucharest", "02": "Bucharest", "03": "Bucharest", "04": "Bucharest", "05": "Bucharest", "06": "Bucharest",
         "07": "Ilfov", "08": "Giurgiu", "10": "Prahova", "11": "Argeș", "12": "Buzău", "13": "Dâmbovița", "14": "Teleorman",
         "20": "Dolj", "21": "Gorj", "22": "Mehedinți", "23": "Olt", "24": "Vâlcea", "30": "Timiș", "31": "Arad",
         "32": "Caraș-Severin", "33": "Hunedoara", "40": "Cluj", "41": "Bihor", "42": "Bistrița-Năsăud", "43": "Maramureș",
         "44": "Satu Mare", "45": "Sălaj", "50": "Brașov", "51": "Alba", "52": "Covasna", "53": "Harghita", "54": "Mureș",
         "55": "Sibiu", "60": "Bacău", "61": "Neamț", "62": "Vrancea", "70": "Iași", "71": "Botoșani", "72": "Suceava",
         "73": "Vaslui", "80": "Galați", "81": "Brăila", "82": "Tulcea", "90": "Constanța", "91": "Călărași", "92": "Ialomița"}
RO_CITY = {"bucharest": "Bucharest", "bucurești": "Bucharest", "brașov": "Brașov", "arad": "Arad", "baia mare": "Maramureș",
           "constanța": "Constanța", "mediaș": "Sibiu", "pitești": "Argeș", "timișoara": "Timiș", "cluj-napoca": "Cluj",
           "iași": "Iași", "oradea": "Bihor", "suceava": "Suceava", "ploiești": "Prahova", "sibiu": "Sibiu", "deva": "Hunedoara",
           "galați": "Galați", "brăila": "Brăila", "târgu mureș": "Mureș", "craiova": "Dolj", "bacău": "Bacău",
           "fălticeni": "Suceava", "câmpeni": "Alba", "sighetu marmației": "Maramureș", "navodari": "Constanța",
           "năvodari": "Constanța", "târgu jiu": "Gorj", "satu mare": "Satu Mare", "alba iulia": "Alba"}


def slug(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def region_of(r):
    cc, reg, city = r["state_code"], (r.get("state") or r.get("region") or "").strip(), (r.get("city") or "").strip()
    if cc == "US": return US.get(reg.upper(), reg)
    if cc == "CA": return CA.get(reg.upper(), reg)
    if cc == "AU": return AU.get(reg.upper(), reg)
    if cc == "GB":
        m = re.match(r"([A-Z]{1,2})(\d+)", (r.get("postal_code") or "").upper().replace(" ", ""))
        if not m: return ""
        area, dist = m.group(1), int(m.group(2))
        if area in GB_SPLIT:
            cut, a, b = GB_SPLIT[area]; return a if dist <= cut else b
        return GB.get(area, "")
    if cc == "ZA": return ZA.get(city.lower(), "")
    if cc == "NZ": return NZ.get(city.lower(), "")
    if cc == "IE": return re.sub(r"^Co\.?\s+", "", reg) or city
    pc = re.sub(r"\D", "", r.get("postal_code") or "")
    if cc == "DE": return DE_CITY.get(city.lower()) or (DE_PLZ.get(pc[:2], "") if len(pc) == 5 else "")
    if cc == "RO": return (RO_PC.get(pc[:2], "") if len(pc) == 6 else "") or RO_CITY.get(city.lower(), "")
    return reg


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 6371 * 2 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))


def main(path=SITE_CSV):
    # path: the site's listings.csv (default) or any CSV with the same columns (e.g. the DE/RO batch before it is appended)
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f); fields = rd.fieldnames; rows = list(rd)
    for r in rows:
        r["region"] = region_of(r)
    # Without a region: the nearest listing with a region in the same country.
    for r in rows:
        if r["region"] or not r.get("latitude"): continue
        p = (float(r["latitude"]), float(r["longitude"]))
        cands = [o for o in rows if o is not r and o["state_code"] == r["state_code"] and o["region"] and o.get("latitude")]
        if cands:
            r["region"] = min(cands, key=lambda o: km(p, (float(o["latitude"]), float(o["longitude"]))))["region"]
            print(f"  nearest: {r['slug']} → {r['region']}")
    missing = [r["slug"] for r in rows if not r["region"]]
    if missing: sys.exit(f"ERROR: no region for {missing}")
    for r in rows:
        r["region_slug"] = slug(r["region"].replace("ß", "ss")); r["country_slug"] = COUNTRY_SLUG[r["state_code"]]
        if not r.get("city"): r["city"] = r["region"]
    for k in ("region", "region_slug", "country_slug"):
        if k not in fields: fields.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    from collections import Counter
    c = Counter((r["state_code"], r["region"]) for r in rows)
    for cc in COUNTRY_SLUG:
        regs = sorted(((reg, n) for (k, reg), n in c.items() if k == cc), key=lambda x: -x[1])
        print(f"{cc}: {len(regs)} regions, ≥3: {sum(1 for _, n in regs if n >= 3)} — " + ", ".join(f"{a} {n}" for a, n in regs))


if __name__ == "__main__":
    main(*sys.argv[1:])
