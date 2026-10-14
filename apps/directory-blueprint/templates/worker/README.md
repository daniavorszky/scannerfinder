# Mail worker: hello@ for the directory

A Cloudflare Email Worker that gives the directory a real address without a mailbox provider. `scripts/mail_worker.py setup` copies this folder to `output/<slug>/worker/` and fills it; nothing in here is edited by hand.

```
Email Routing (hello@) ──► email()  ──► fixed acknowledgement to the sender (Email Sending, from SEND_FROM)
Claim form (POST /claim) ─► fetch()  ──► KV queue ──► Claude triage ──► review email to REVIEW_TO with a link to
                                                                        GET/POST /approve/:id/:token (the review page: Send or Ignore)
                                                     GET /inbox, POST /inbox/:id (the same queue for scripts/mail_inbox.py)
```

What the triage returns for each message: a category (claim of an existing listing, new listing request, correction, removal request, featured enquiry, consumer enquiry, vendor or link pitch, spam, other), the listing it is about if any, three checks (email domain matches the website, phone matches a listing, business already in the directory), what is still missing, a two-sentence summary, and a draft reply. The draft never promises a listing, a change, a feature or a link; it may state the tier prices from `TIERS` and nothing else about money. The email body is treated as untrusted data.

The worker never changes a listing. A reply goes to a sender only from the review page or `scripts/mail_inbox.py --send`, on the owner's word; every reply sent is blind-copied to `REVIEW_TO`.

## Setup

Runs from the Blueprint root, after Gate 6 (the site is live, the domain's DNS is in the same Cloudflare account, `npx wrangler login` was done). The owner's part first:

1. Cloudflare dashboard, the account: **Workers & Pages → Plans**, buy **Workers Paid** ($5 a month; covers the worker, Email Routing and Email Sending).
2. **Email Service → Email Sending → Enable**, and add the directory's **root domain** as a sending domain (not the suggested `mail.` subdomain: replies to a subdomain address bounce, because nothing receives there). Cloudflare writes the DKIM, SPF and DMARC records. Leave its DMARC record alone and never add a second one.
3. An Anthropic API key from console.anthropic.com, saved in the owner's own Terminal: `python3 scripts/mail_worker.py save-key anthropic --slug <slug>` (asks for the key hidden, tests it, saves it to the keychain). `python3 scripts/mail_worker.py keys --slug <slug>` prints that command.

Then Claude Code: `python3 scripts/mail_worker.py setup --slug <slug> --review-to <owner's inbox>` fills `wrangler.jsonc` from `site.json` (brand, domain, hello@ address, tier prices, the trade's name words the matcher ignores), writes `src/listings.json`, creates the KV namespace, sets the two secrets (`ANTHROPIC_API_KEY`, and `INBOX_KEY`, generated), deploys, records `WORKER_URL`, and posts one test claim. Deploys use the `wrangler login`; a token saved with `save-key cloudflare` (or `CLOUDFLARE_API_TOKEN`) overrides it, for an owner with two Cloudflare accounts.

Last, the owner again: the domain's **Email → Email Routing → Get started**, then **Routing rules → Create address**: `hello` → **Send to a Worker** → the worker's name. Catch-all off.

`python3 scripts/mail_worker.py wire-form --slug <slug>` points the site's claim form at the worker (`contact.formEndpoint`); then Gate 5 and a site deploy. After any listings change: `python3 scripts/mail_worker.py deploy --slug <slug>` (listings.json refreshed, worker redeployed).

## The queue

```
python3 scripts/mail_inbox.py --slug <slug>                  # open items, with drafts
python3 scripts/mail_inbox.py --slug <slug> --send <id>      # send the draft as it stands
python3 scripts/mail_inbox.py --slug <slug> --send <id> --text-file reply.txt
python3 scripts/mail_inbox.py --slug <slug> --ignore <id>
python3 scripts/mail_inbox.py --slug <slug> --retriage <id>  # after a change to src/templates.ts or the matcher
```

The tone of the drafts is `src/templates.ts` (one function). Change it, `deploy`, then `--retriage` the open items.

## Costs and guards

Workers Paid $5 a month. Each triage is one short call on `claude-opus-5-5` (about 1,500 input and 300 output tokens, under a cent). No acknowledgement to automated mail (Auto-Submitted, Precedence bulk or list, noreply and mailer-daemon senders), and the acknowledgement itself is marked Auto-Submitted. The claim form's honeypot (`_gotcha`) drops bots silently; `_noack` re-enters an old submission without an acknowledgement. Queue items expire after 90 days and are readable only with `INBOX_KEY`. Bodies are cut at 6,000 characters before triage.
