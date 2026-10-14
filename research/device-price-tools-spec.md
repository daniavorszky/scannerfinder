# Spec — Device Price Index (Glassdoor) + ROI Calculator

Status: prototype local (2026-10-12). Hosting nedecis (pasul 2). Prototip: [apps/price-tools/index.html](../apps/price-tools/index.html). Seed: [data/device-prices-seed.csv](../data/device-prices-seed.csv). Context: [proprietary-data-ideas.md](proprietary-data-ideas.md).

Limba: engleză (site-ul e în engleză). Branding preluat de pe scannerfinder.com (SpreadSimple): fundal slate `#272A31` / `#3B414C` / `#474955`, accent coral `#FF422F`, text alb, gri `#A2A9B4`, font Nunito Sans, colțuri 4px.

## Unealta 1 — „What did practitioners pay?” (Device Price Index)

**Ce vede oricine (gratuit):** pe brand, intervalul din surse publice (seed) + câte rapoarte de la practicieni există. Pentru NES, MORA, TimeWaver: „No public price exists — be the first to report”. Lipsa prețului e ea însăși argumentul.

**Ce se deblochează:** tabelul cu rapoartele practicienilor (model, an, nou/second-hand, preț plătit, țară, abonament lunar, finanțare, satisfacție) + medianele pe model.

**Condiția de deblocare:** practicianul trimite propriul raport. Prototip: deblocare per browser. Producție: email verificat (link magic) + deblocare 90 de zile, reînnoită la un nou raport.

**Câmpuri raport (obligatoriu \*):**
- Brand\*, model\*, anul achiziției\*, condiție\* (new / used / lease / rental)
- Preț plătit\* + monedă\*; inclus training? (y/n)
- Abonament software lunar
- Țara\*, rol (practitioner / clinic owner / prospective buyer)
- Satisfacție cu producătorul 0–10
- Plan în 12 luni\*: keep / upgrade same brand / switch brand / sell / undecided
- Email\* (verificare + raport)
- Consimțăminte separate, nebifate implicit: (1) publicare agregată și anonimizată (obligatoriu pentru trimitere); (2) contact de la producători/distribuitori cu oferte (opțional — asta e lista vândută).

**Reguli de date:**
- Mediana se afișează doar la n ≥ 5 rapoarte pe model (k-anonimitate). Sub prag: „3 reports — 2 more to unlock the median”.
- Valorile aberante (>3× sau <⅓ din mediana brandului) intră în review, nu în public.
- Nu se publică niciodată email, nume sau cabinet lângă un preț.
- Fără câmpuri medicale.

## Unealta 2 — „Will a scanner pay for itself?” (ROI Calculator)

**Intrări (valori implicite din seed, per brand):** prețul aparatului, training/certificare, abonament lunar, alte costuri lunare, preț ședință, ședințe/săptămână, săptămâni lucrate/an (implicit 46), marjă opțională din produse pe ședință.

**Formule:**
- Sesiuni/lună = ședințe/săpt × săptămâni/an ÷ 12
- Venit lunar = sesiuni/lună × (preț ședință + marjă produse)
- Net lunar = venit lunar − abonament − alte costuri
- Recuperare (luni) = (aparat + training) ÷ net lunar (dacă net ≤ 0 → „never at these numbers”)
- Ședințe/săpt necesare pentru recuperare în 12 luni = ((aparat + training) ÷ 12 + costuri lunare) ÷ (preț + marjă) ÷ (săptămâni/an ÷ 12)
- Profit an 1 = net lunar × 12 − investiție inițială

**Captura (după rezultat):** „Email me the full comparison + real practitioner prices”: email\*, țară\*, buget, termen de cumpărare (0–3 / 3–6 / 6–12 luni / just researching), background (naturopath, chiropractor, nutritionist, coach, other), branduri luate în calcul. Consimțământ separat pentru contact de la distribuitori.

## Ce valorează datele (de ce construim asta)

- Rapoartele → indice de preț pe aparate (nu există public) + bază instalată + **intenție de schimbare** → raport pentru producători.
- Calculatorul → lead-uri cu intenție de cumpărare de 5–20k $ → comision de referral (model în [proprietary-data-ideas.md](proprietary-data-ideas.md)).

## Deschis

- Hosting + bază de date (pasul 2). Prototipul stochează local (localStorage) — fără trimitere externă.
- Site-ul live încă promovează iTOVi („Find a ZYTO or iTOVi near you”), iar planul exclude iTOVi → de aliniat.
- Cursurile valutare din prototip sunt fixe și aproximative (GBP 1.30, EUR 1.15, CAD 0.73, AUD 0.66) — de înlocuit cu un feed la producție.
