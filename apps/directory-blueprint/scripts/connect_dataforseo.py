#!/usr/bin/env python3
"""Connect DataForSEO to Claude Code from your own Terminal. The member runs this, never Claude.

  python3 scripts/connect_dataforseo.py        (on Windows: python scripts\\connect_dataforseo.py)

It asks for the API login and the API password from https://app.dataforseo.com/api-access (the
password stays hidden while you type or paste it), checks them against DataForSEO (free), and
only then saves them with `claude mcp add -s user dataforseo ...`, which is where the Blueprint's
scripts and the DataForSEO tools in Claude Code read them from (~/.claude.json). Nothing is
written into this folder, and nothing goes through the chat.

It exists because the by-hand command fails in three ordinary ways (first live run, 2026-10-01):
the Terminal cannot find `claude`, a password with a special character is cut by the shell unless
it is in single quotes, and the account password gets typed where the API password belongs. This
script finds `claude` itself, passes the values without a shell, and tests the login before saving.

  python3 scripts/connect_dataforseo.py --check     # is a working login saved? prints yes or no, never the login
"""
import argparse, base64, getpass, json, os, shutil, subprocess, sys, urllib.error, urllib.request

USER_DATA = "https://api.dataforseo.com/v3/appendix/user_data"
HERE = os.path.dirname(os.path.abspath(__file__))


def find_claude():
    """The claude command, wherever the installer put it. A fresh Terminal often has no path to it."""
    found = shutil.which("claude")
    if found:
        return found
    home = os.path.expanduser("~")
    for p in (os.path.join(home, ".local", "bin", "claude"), os.path.join(home, ".claude", "local", "claude"),
              "/opt/homebrew/bin/claude", "/usr/local/bin/claude",
              os.path.join(home, ".local", "bin", "claude.exe"),
              os.path.join(os.environ.get("APPDATA", ""), "npm", "claude.cmd")):
        if p and os.path.isfile(p):
            return p
    return None


def test_login(login, password):
    """(ok, message). One free request to DataForSEO's account endpoint."""
    auth = "Basic " + base64.b64encode(f"{login}:{password}".encode()).decode()
    req = urllib.request.Request(USER_DATA, headers={"Authorization": auth})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return False, ("DataForSEO rejected that login. The API password is not the password you sign in with: "
                           "copy both values from app.dataforseo.com/api-access (Reset API password emails a new one) and run this again.")
        return False, f"DataForSEO answered {e.code}. Try again in a minute."
    except Exception as e:
        return False, f"Could not reach DataForSEO ({e}). Check the internet connection and run this again."
    if data.get("status_code") != 20000:
        return False, f"DataForSEO error {data.get('status_code')}: {data.get('status_message')}"
    res = ((data.get("tasks") or [{}])[0].get("result") or [{}])[0]
    balance = (res.get("money") or {}).get("balance")
    return True, ("Login accepted." + (f" Balance: ${balance:,.2f}." if isinstance(balance, (int, float)) else ""))


def ask(prompt, hidden=False):
    if not sys.stdin.isatty():          # piped input, for tests: one value per line
        return sys.stdin.readline().strip()
    return (getpass.getpass(prompt) if hidden else input(prompt)).strip()


def strip_quotes(v):
    return v[1:-1] if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"" else v


def main():
    ap = argparse.ArgumentParser(description="Save your DataForSEO API login in Claude Code's settings, from your own Terminal.")
    ap.add_argument("--check", action="store_true", help="say whether a working login is already saved, and exit")
    ap.add_argument("--name", default="dataforseo", help=argparse.SUPPRESS)
    a = ap.parse_args()

    if a.check:
        sys.path.insert(0, HERE)
        import fetch_dataforseo as f
        auth = f.load_credentials()      # exits with the how-to when nothing is saved
        req = urllib.request.Request(USER_DATA, headers={"Authorization": auth})
        try:
            urllib.request.urlopen(req, timeout=60).read()
        except urllib.error.HTTPError as e:
            sys.exit(f.REJECTED if e.code == 401 else f"DataForSEO answered {e.code}. Try again in a minute.")
        except Exception as e:
            sys.exit(f"Could not reach DataForSEO ({e}). Check the internet connection and run this again.")
        print("A working DataForSEO login is saved on this computer.")
        return

    claude = find_claude()
    if not claude:
        sys.exit("Claude Code's command was not found on this computer. Install it first (claude.com/claude-code, "
                 "or the Setup lesson in the classroom), open a new Terminal window, then run this again.")

    print("DataForSEO API login. Both values are on app.dataforseo.com/api-access.")
    login = strip_quotes(ask("API login (your DataForSEO email): "))
    password = strip_quotes(ask("API password (hidden while you type or paste, then Return): ", hidden=True))
    if not login or not password:
        sys.exit("Both values are needed. Nothing was saved.")

    ok, msg = test_login(login, password)
    print(msg)
    if not ok:
        sys.exit("Nothing was saved.")

    server = ["cmd", "/c", "npx", "-y", "dataforseo-mcp-server@latest"] if os.name == "nt" else ["npx", "-y", "dataforseo-mcp-server@latest"]
    removed = subprocess.run([claude, "mcp", "remove", "-s", "user", a.name], capture_output=True, text=True).returncode == 0   # replace an older entry, if any
    add = subprocess.run([claude, "mcp", "add", "-s", "user", a.name,
                          "-e", f"DATAFORSEO_LOGIN={login}", "-e", f"DATAFORSEO_PASSWORD={password}", "--", *server],
                         capture_output=True, text=True)
    if add.returncode != 0:
        detail = (add.stderr or add.stdout or "").replace(password, "***").strip()
        sys.exit(f"Claude Code could not save the connection: {detail}\n"
                 + ("The earlier entry was removed and no new one was saved. Run this again." if removed else "Nothing was saved."))

    # Read it back. On Windows the claude command can be a .cmd file, and cmd.exe changes a value that
    # holds one of & % ^ | < > on the way through; a login saved wrong is worse than one not saved.
    saved = {}
    try:
        with open(os.path.expanduser("~/.claude.json"), encoding="utf-8") as fh:
            saved = ((json.load(fh).get("mcpServers") or {}).get(a.name) or {}).get("env") or {}
    except Exception:
        pass
    if saved and (saved.get("DATAFORSEO_LOGIN") != login or saved.get("DATAFORSEO_PASSWORD") != password):
        subprocess.run([claude, "mcp", "remove", "-s", "user", a.name], capture_output=True, text=True)
        sys.exit("The login was changed on its way into Claude Code's settings (a symbol in the password, most likely), so the entry was removed again. "
                 "Reset the API password at app.dataforseo.com/api-access to one without & % ^ | < >, then run this again.")

    print("Saved in Claude Code's settings (not in this folder).")
    if not shutil.which("npx"):
        print("Note: Node.js was not found. The Blueprint's pull works without it; the DataForSEO tools inside Claude Code need it (nodejs.org).")
    print("Go back to Claude and reply: done")


if __name__ == "__main__":
    main()
