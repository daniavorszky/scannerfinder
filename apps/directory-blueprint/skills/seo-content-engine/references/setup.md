# DataForSEO Setup (Stage 0)

Ask ONE thing per turn and keep every message short. DataForSEO is required — never
offer a "no DataForSEO" or web-search path. **Never print the credential value, and
never accept a credential in chat** (details below).

## Step 1 — check for an existing connection FIRST

Before reading any file, check whether DataForSEO is already connected in this session.
**Detect it by tool NAME, not server prefix:** if any loaded tool's name contains a
DataForSEO operation this skill uses (`serp_organic_live_advanced`,
`on_page_instant_pages`, `on_page_content_parsing`, `dataforseo_labs_ranked_keywords`,
`appendix/user_data`), DataForSEO is connected — regardless of prefix. A claude.ai
connector exposes them under a UUID prefix (`mcp__<uuid>__…`); a CLI-added server uses
its own name. NEVER require a literal `dfs-mcp:` prefix. Don't run `claude mcp list` or
hunt for the `claude` binary.

- **DataForSEO tools ARE loaded → live connection.** Run one free smoke-test call
  (`appendix/user_data`, which also returns balance) to confirm auth, then go to the
  hand-off. **Do NOT read `credentials.md` and do NOT ask for any credential.** (Quiet
  balance check: silent if healthy; only warn if low — about $0.50 or less — since Stage
  1 makes ~20+ billable calls.)
- **No DataForSEO tools loaded → fall back to `references/credentials.md`** (Step 2).

## Step 2 — the credentials file (fallback only)

Only reached when no DataForSEO tools are loaded. `references/credentials.md` holds
either a `login` + `password`, or a `base64_token`. The MCP reads `.claude.json`, so
when credentials are set, the skill encodes them if needed and syncs an entry there.

- **File is blank** → not set up. Go to **Connect / update**.
- **File has credentials** →
  > I found saved DataForSEO credentials in `references/credentials.md`. Reply **1** to
  > use them, or **2** to update them.
  - **Reply 1 (use):** **Sync** the credential into `.claude.json`, **Validate** (one
    `appendix/user_data` call — show login + balance), then **Restart** so the tools
    load. (Quiet balance rule as above.)
  - **Reply 2 (update):** the user edits the file (see **Connect / update**, option 2),
    then Sync / Validate / Restart. If the new credential equals the stored one, skip.

## Connect / update

Message (two options, reply with the number):

> DataForSEO needs connecting. Two ways:
>
> **Option 1 (recommended, most secure) — install it yourself.** Add the DataForSEO
> MCP as a claude.ai connector, or via `claude mcp add`, so the skill never handles your
> secret. Guide:
> https://dataforseo.com/help-center/3-ways-to-install-dataforseo-mcp-with-claude-code
>
> **Option 2 — put your credentials in the file.** Open `references/credentials.md` in
> your editor, fill in your `login` + `password` (or `base64_token`) from the API Access
> tab (https://app.dataforseo.com/api-access), save, and reply **Continue**. I'll sync
> and connect it.
>
> Reply **1** or **2**.

- **Reply 1 (self-install):** one short reply, then wait —
  > Once it's installed, fully restart Claude Code and reply **Continue** — I'll re-check
  > the connection (Step 1).
- **Reply 2 (file):** tell the user to fill in `references/credentials.md`, save, and
  reply Continue — then read the file and go to **Sync**.

**Never accept a credential pasted into chat.** Do not ask the user to paste a
login:password or Base64 token, and do not offer to "wire it up" from a pasted value — a
pasted token lands in plaintext in the session transcript, and Base64 decodes to the raw
login and password. If a user pastes a credential anyway, **refuse to use it**: tell them
to remove it from the chat, put it in `references/credentials.md` instead, and rotate it
(it's now exposed). Credentials only ever enter via the file (Option 2) or the user's own
MCP install (Option 1).

## Sync (write to .claude.json)

1. Get the Base64 token: if you have `login:password`, encode it —
   - macOS/Linux: `printf '%s' "login:password" | base64`
   - Windows PowerShell: `[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("login:password"))`
   - If you already have a token, use it as-is.
2. Validate BEFORE writing anything (see **Validate** below). Only continue if it
   passes.
3. Add the server (user scope so it works in every project):
   `claude mcp add -s user --header "Authorization: Basic <token>" --transport http dfs-mcp https://mcp.dataforseo.com/http`
   - If `claude` isn't recognized (not on PATH), either ask the user to paste that
     command into the VS Code integrated terminal, or edit the config directly:
     read `.claude.json` (macOS/Linux `~/.claude.json`, Windows
     `$env:USERPROFILE\.claude.json`) and add this under the top-level
     `mcpServers`, preserving everything else exactly:
     ```json
     "dfs-mcp": {
       "type": "http",
       "url": "https://mcp.dataforseo.com/http",
       "headers": { "Authorization": "Basic <token>" }
     }
     ```

## Validate (use the ACCOUNT endpoint, not SERP/keywords)

Make ONE free call to the account endpoint. It confirms the login works regardless
of which paid APIs the account has enabled — unlike SERP/keywords endpoints, which
can return 403 on a fresh or low-balance account even with valid credentials.

- macOS/Linux:
  `curl -s -H "Authorization: Basic <token>" https://api.dataforseo.com/v3/appendix/user_data`
- Windows PowerShell:
  `Invoke-RestMethod -Uri "https://api.dataforseo.com/v3/appendix/user_data" -Headers @{Authorization="Basic <token>"}`

- `status_code` 20000 → valid. Read `login` and `money.balance` from the response.
- HTTP 401 or `status_code` 40101 → credentials are wrong. Say so and ask them to
  paste again (or re-check the file). Do not continue.

## Show the account (do this after every successful validate/verify)

Before handing off, show the user which account is connected and its balance — one
short line, so they can confirm the right account and see their funds:

> Connected to DataForSEO account **[login]** — balance **$[balance]**.

The `login` is an account identifier, not the secret credential, so it's fine to
show; never show the password or token. If the balance is very low (about $1 or
less) or the account looks like an unverified free trial, add one line: the
connection works, but live keyword/SERP calls in Stage 1–2 may return 403 until the
account is funded or verified.

## Restart + verify

After Sync, tell the user (one line):
> Wired up and your credentials check out. Now fully restart Claude Code and reply
> **Continue** — I'll confirm the connection and we'll start.

On the next run, the DataForSEO tools should be visible (match by name, any prefix —
see Step 1). Confirm auth with one
free account call (`appendix/user_data`, via `dfs-mcp` or direct) so you also get
the login and balance:
- Returns cleanly → connected; run **Show the account**, then go to hand-off.
- Auth failure → credentials are wrong; go to **Connect / update** (Option 2).
- Tools still not visible → restart didn't take or setup didn't save; ask them to
  confirm a full restart, or retry setup.

## Hand-off to Stage 1 (one short message)

Show the account line first (from **Show the account**), then ask the one question:

- Started WITH a topic:
  > You started with "[topic]" — is that the main phrase you want to rank for?
  > Reply **yes**, or give me a better one.
- Started WITHOUT a topic:
  > Connected. What do you want to write about? That's the main phrase you want to
  > rank for — e.g. "best CRM for small business", or a broader topic like
  > "email marketing tips".

Ask nothing else in that message. Stage 1 then continues one step per turn.
