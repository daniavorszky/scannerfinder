---
status: active
owner: Dan Iavorszky
claude_role: Construiește site-ul scannerfinder.com pe baza kitului (Astro → Cloudflare Pages), adaptat la 7 țări și la nișa wellness. Întreabă înainte de cheltuieli DataForSEO, deploy, înregistrare domeniu/conturi, Stripe și orice contact cu cabinetele.
last_updated: 2026-10-12
---

# Directory Blueprint (Rank Expand Academy) — kitul de construcție

## Purpose

Kit terț (Rank Expand Academy, versiunea din 2026-10-05) care transformă un export Google Maps într-un director local static, monetizabil: Astro → Cloudflare Pages, 6 porți (Scope → Clean → Enrich → Plan → Build → Launch lean), cu șablon complet, site de referință (1.719 pagini HTML), formular de revendicare, niveluri featured (Stripe Payment Links) și un mail worker opțional. Aici e motorul pentru pasul 2 din [proiect](../../_overview.md): directorul public.

## Load First

- [CLAUDE.md](CLAUDE.md) al kitului: regulile și cele 6 porți. Se încarcă automat când sesiunea rulează din folderul ăsta.
- [wiki/index.md](wiki/index.md): catalogul framework-ului.
- [README.md](README.md): pașii de rulare și costurile măsurate.
- Proiectul: [_overview.md](../../_overview.md). Fișierul master de date: [listings_enriched.csv](../../data/listings_enriched.csv) (844 de listări).

## Adaptări necesare (kitul presupune o nișă și un stat din SUA)

| Kitul presupune | ScannerFinder are | Ce facem |
|---|---|---|
| 1 stat SUA, pagină-hub de stat | 7 țări (US, GB, CA, AU, ZA, IE, NZ) | hub pe țară în loc de stat; slug-uri `/us/`, `/gb/`… |
| Poarta 1 trage datele din DataForSEO | extragerea e deja făcută (2026-10-11, $6.61) | sărim peste pull; scope-ul îl scriem manual |
| Coloane în formatul Outscraper | schema noastră (`title`, `url`, `region`…) | un script de conversie → `input/listings-raw.csv` |
| Poarta 2 filtrează după stat | curățarea noastră e deja făcută (844 incluse) | rulăm doar dedupe/thin, fără filtrul de stat |
| „Service pages” = atribute | branduri de aparate (ZYTO, NES, BICOM…) | pagini pe brand și pe brand × țară |
| Fact sheet cu licențe/permise de stat | nișă fără validare clinică | fact sheet pe reglementări de afirmații wellness (FDA/FTC, MHRA/ASA, TGA etc.) |
| Lista de interdicții a kitului | registru „wellness”, niciodată „diagnostic/tratament” | adăugăm cuvinte medicale în `scripts/copy-bans.txt` |
| ZIP → județ (doar SUA) | 7 țări | se omite; kitul are fallback |

## Verificare de securitate (2026-10-12)

Codul vorbește doar cu DataForSEO, Cloudflare, Anthropic (mail worker), Stripe (linkuri), Formspree, npm. Credențialele nu se salvează în folder: DataForSEO din `~/.claude.json`, cheia Anthropic în keychain, iar `connect_dataforseo.py`/`save-key` le rulează Dan în propriul Terminal. Kitul cere `npm install` la poarta 5, adică instalare de pachete terțe (Red, de cerut aprobare atunci).

## Housekeeping

- Nu edita fișierele kitului (`scripts/`, `templates/`, `wiki/framework/`). Adaptările stau în `output/<slug>/` sau în scripturile proiectului, ca un update de kit să poată fi suprapus.
- Build-ul stă în `output/<slug>/` (slug propus: `scannerfinder`). `site/dist/` e folderul de deploy și nu se editează de mână.
- `wiki/log.md` e jurnalul kitului; deciziile proiectului stau în [_overview.md](../../_overview.md) al proiectului.

## Archive Criteria

Se arhivează când site-ul e live și operarea trece în `02-areas/scannerfinder-com/`, sau dacă Dan alege alt stack.
