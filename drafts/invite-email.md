# Invitație revendicare profil — tier A (draft)

Status: **draft, netrimis** (2026-10-12). Trimiterea e Red → aprobare Dan.
Liste (generate cu [build_invites.py](../scripts/build_invites.py)):
- **Email:** [invite_tier_A_email.csv](../data/invite_tier_A_email.csv) — 53 (US 37, AU 9, CA 4, NZ 3).
- **Formular de contact / telefon:** [invite_tier_A_contact.csv](../data/invite_tier_A_contact.csv) — 33 (GB 26, ZA 2 din motive legale + 5 US fără email valid). 29 au pagină de contact, 1 doar telefon. Atenție: Restoration Wellness — site-ul afișează conținut de landscaping, de sărit.
- Adrese respinse/păstrate manual: [email_overrides.csv](../data/email_overrides.csv).
Merge tags = coloane din CSV: `{{business_name}}`, `{{city}}`, `{{country_name}}`, `{{device_phrase}}`, `{{profile_clause}}`, `{{search_volume}}`, `{{claim_url}}`.

## Logica

- **O singură acțiune:** verifică și revendică profilul (2 minute). Nu cerem nimic altceva în primul email.
- **Ce primesc:** clienți care caută deja (volum real de căutări din țara lor), listare gratuită primul an, apar înaintea profilurilor nerevendicate în orașul lor.
- **De ce acum:** profilul e deja pre-completat din site-ul lor → efort aproape zero; corectează dacă e greșit.
- **Price Index** doar în P.S. — e cârligul pentru a doua acțiune, nu o distragem pe prima.
- Fără afirmații medicale. Fără „diagnostic”, „treat”, „heal”.
- Opțiune clară de ieșire („reply remove”) — reduce reclamațiile de spam și ține lista curată.

---

## Email 1 — ziua 0

**Subiect (A/B):**
1. `{{business_name}} on ScannerFinder`
2. `Is this right, {{business_name}}?`
3. `People in {{city}} searching for {{device_phrase}}`

**Preheader:** `Your profile is pre-filled. 2 minutes to check it.`

```
Hi {{business_name}} team,

I'm Dan, founder of ScannerFinder. About {{search_volume}} people a month in {{country_name}} search Google for scans like yours, and there's no single place that lists the practitioners who offer them. We're building it.

I've already set up a profile for {{business_name}} from your website, with {{profile_clause}}. Prices only go live once you confirm them.

Could you take 2 minutes to check it's accurate?

{{claim_url}}

Claiming is free, no card needed. Claimed profiles show above unclaimed ones in {{city}} results, and you can add your booking link, photos and prices.

If you'd rather not be listed, just reply "remove" and I'll take it down the same day.

Dan Iavorszky
ScannerFinder.com

P.S. Practitioners who claim their profile get early access to the Device Price Index: what other practitioners actually paid for their device and what they charge per session. Nobody publishes this today.
```

## Email 2 — ziua 4 (doar celor care n-au deschis linkul)

**Subiect:** `Re: {{business_name}} on ScannerFinder`

```
Hi again,

Quick follow-up on your ScannerFinder profile. It's pre-filled with {{profile_clause}}, and it takes about 2 minutes to confirm or correct.

{{claim_url}}

Once claimed, you control what's shown, and your profile ranks above unclaimed practitioners in {{city}}.

Not for you? Reply "remove".

Dan
```

## Email 3 — ziua 10 (ultimul)

**Subiect:** `Closing the loop`

```
Hi,

Last note from me. I'll keep {{business_name}} as a basic listing (name, city and phone) so people can still find you.

If you ever want to add your prices, booking link and the device you use, your profile is here:
{{claim_url}}

And if you'd prefer not to appear at all, reply "remove".

Dan
```

## Footer (toate emailurile)

```
ScannerFinder.com · Str. Popa Tatu 59/1, Sector 1, Bucharest, Romania
You're receiving this because your practice email is published on your website. Reply "remove" or unsubscribe: {{unsubscribe_url}}
```

## Varianta pentru formularul de contact (GB / ZA / fără email)

Fără footer de unsubscribe (nu e email în masă), mai scurtă — câmpurile de formular au limită.

```
Hi {{business_name}} team,

I'm Dan, founder of ScannerFinder, a new directory of practitioners who offer {{device_phrase}} and similar services. About {{search_volume}} people a month in {{country_name}} search for scans like yours.

I've set up a free profile for {{business_name}} from your website, with {{profile_clause}}. Could you check it's accurate? It takes 2 minutes:
{{claim_url}}

Free for the first year. If you'd rather not be listed, reply "remove" and I'll take it down.

Dan Iavorszky, ScannerFinder.com
```

---

## Exemplu randat (rând real din listă)

> **Subiect:** Gold Country Wellness on ScannerFinder
>
> Hi Gold Country Wellness team,
>
> I'm Dan, founder of ScannerFinder. About 13,000 people a month in the US search Google for scans like yours, and there's no single place that lists the practitioners who offer them. We're building it.
>
> I've already set up a profile for Gold Country Wellness from your website, with your QEST4 scans, Loomis location and $250 session price.
>
> Could you take 2 minutes to check it's accurate? …

## Înainte de trimitere — de decis / de pregătit

1. **`{{claim_url}}`** — decis 2026-10-12: se adaugă ulterior, odată cu pagina de revendicare (pasul 2). Până atunci nu se trimite nimic.
2. ~~Adresa poștală~~ — decis: Str. Popa Tatu 59/1, Sector 1, Bucharest, Romania (în footer).
3. **Domeniu de trimitere:** decis `m.scannerfinder.com` (ex. `dan@m.scannerfinder.com`). DNS-ul e la idagency.ro. Domeniul principal are acum **null MX** (`MX 0 .` = nu primește email) și fără DMARC → subdomeniul are nevoie de: căsuță reală (Google Workspace / Zoho, ca să primească răspunsurile „remove”), MX, SPF, DKIM, DMARC (`p=none` la început), CNAME de tracking dacă unealta de trimitere îl cere. Apoi warm-up ~2–3 săptămâni.
4. **Legal pe țări** (orientativ, nu e consultanță juridică — de confirmat):
   - **US (39):** CAN-SPAM — OK cu opt-out + adresă poștală.
   - **CA (4), AU (9), NZ (3):** consimțământ implicit/dedus pentru adrese de business publicate vizibil, dacă mesajul ține de activitatea lor — OK, cu unsubscribe.
   - Decis 2026-10-12: email doar US/CA/AU/NZ; GB și ZA prin formularul de contact.
   - **GB (26):** PECR — firmele (Ltd) sunt OK cu opt-out, dar **comercianții individuali (sole traders) cer consimțământ prealabil**. Mulți practicieni sunt sole traders. Recomandare: GB doar adrese pe domeniu propriu de la firme vizibil Ltd, restul prin formularul de contact de pe site sau telefon.
   - **ZA (2):** POPIA cere consimțământ pentru marketing direct → nu trimitem email; formular de contact.
5. ~~4 adrese `third-party?`~~ — verificate 2026-10-12: 2 respinse (placeholder de template `hi@mystore.com`; domeniu de landscaping), 1 păstrată (adresa e pe propriul profil Google), 1 trece pe formular (GB).
6. **Ritm:** max. ~20–30 emailuri/zi de pe un domeniu nou, începând după warm-up.
