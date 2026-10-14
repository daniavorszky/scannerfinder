---
title: Mail worker
type: framework
status: current
updated: 2026-10-09
---

# Mail worker: hello@ with Claude triage

After launch and optional. A Cloudflare Email Worker (`templates/worker/`, copied and filled by `scripts/mail_worker.py setup`) gives the directory a real address, hello@yourdomain.com, without a mailbox provider, and keeps the one rule in [[refresh-and-upkeep]]: every claim is checked by a person before anything on the site changes. The worker removes the two slow parts, the first reply and the research.

## What it does with every message

Mail to hello@ (Cloudflare Email Routing) and every claim form submission (`POST /claim`) take the same path:

1. A fixed acknowledgement to the sender within a minute: the message arrived, a person checks every request, a reply within a day. None to automated mail.
2. A Claude triage, one short call: category (claim of an existing listing, new listing request, correction, removal request, featured enquiry, consumer enquiry, vendor or link pitch, spam, other), the listing it is about (matched by a pasted listing address, phone, website host or the name's distinctive words), three checks (email domain matches the website, phone matches a listing, business already in the directory), what is still missing, a two-sentence summary, a draft reply. The email body is untrusted data; instructions inside it are never followed.
3. A review email to the member with all of that and a link to a review page: the draft in an editable box, **Send this reply** and **Ignore**. Every reply sent is blind-copied to the member.

What it never does: add, change or remove a listing; send a draft on its own; promise a link, a listing or a placement. The draft may state the tier prices from `site.json` and nothing else about money. Listing changes stay CSV, Gate 5, redeploy ([[refresh-and-upkeep]]), and the worker is redeployed after them so its matching list is current.

## The verification rule in the drafts

The member checks a claim with one of two things: a reply from an address on the business's website domain, or a phone number that matches its Google listing ([[monetization-slots]], the claim flow). The draft asks for at most one of those, in one friendly sentence, only when neither is present. It never asks for written authorization, proof of role or documents, and never tells an agency sender that their authority is unverified; that goes in the summary for the member. The first version of the prompt demanded authorization and was softened the same day (2026-10-09). The prompt is one function in `src/templates.ts`.

## Setup, in order

Member, in the Cloudflare dashboard: Workers Paid ($5 a month), then Email Sending enabled on the **root domain** (the suggested `mail.` subdomain has no inbox, so replies to it bounce; that happened on the first run), leaving Cloudflare's DMARC record alone. Member, in their own Terminal: the Anthropic key, through the `save-key` command Claude Code prints (`scripts/mail_worker.py keys`): the command asks for the key after it starts, so the clipboard order cannot go wrong. Claude Code: `scripts/mail_worker.py setup --slug <slug> --review-to <address>` (config from `site.json`, `listings.json`, KV, secrets, deploy, `WORKER_URL`, one test claim). Member, in the dashboard: the domain's Email Routing rule `hello` → the worker, catch-all off. Claude Code: `wire-form`, Gate 5, deploy. Deploys use the Gate 6 `wrangler login`, whose default scopes cover Workers, KV and Pages; a Cloudflare API token is needed only for a member who deploys with a token (two accounts), and then it needs Workers Scripts: Edit and Workers KV Storage: Edit as well as Cloudflare Pages: Edit, made in the account that holds the directory.

Email Routing replaces the domain's MX records, so it cannot share a domain with a mailbox provider. The Blueprint's directories have none on the directory domain; a member who does uses a subdomain for the directory address and sets `MAIL_ADDRESS` and `SEND_FROM` to it.

## Costs

Workers Paid covers the worker, Email Routing and Email Sending. A triage is about 1,500 input and 300 output tokens on `claude-opus-5-5`, under a cent; a directory with a few messages a day is cents a month.

## Troubleshooting, from the first run

- Wrangler says authentication error though the token verifies: the token was made in a different Cloudflare account from the one that holds the directory. Make it in the account whose Workers & Pages page lists the directory.
- The saved Anthropic key starts with `cfat_`, or the check returns 401: the Cloudflare token was pasted at the Anthropic prompt. `save-key` refuses a key that does not answer; run it again.
- Triage fails with invalid x-api-key right after setup: the secret had not rolled out. Wait a minute, `mail_inbox.py --retriage <id>`.
- A reply to a review email bounces with address not found: sending is from a subdomain with no inbox. Enable Email Sending on the root domain; `SEND_FROM` is hello@ on the root domain.
- The acknowledgement lands in spam with SPF, DKIM and DMARC passing: a new sending domain. Mark Not spam, add the address to contacts, carry on.
- The draft asks for what the sender already gave: the matcher did not read a pasted address or a form field. Fix the matcher in `src/index.ts`, `deploy`, `--retriage`.
- Two DMARC records on the domain: one added by hand beside Cloudflare's. Delete the hand-made one; two make the policy invalid.
- A key showed on screen: disable it in its dashboard, make a new one, `save-key` again, `setup` again (it re-sets the worker secret).
- Anything else: `npx wrangler tail` in the worker folder while a test email is sent.
