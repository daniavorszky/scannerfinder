#!/bin/sh
# Double-click this file on a Mac to look at the reference site in your browser.
# It serves the site folder beside it from your own computer. Close the window to stop it.
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed. Get it at python.org, then open this file again."
  printf "Press Return to close. "; read _; exit 1
fi
exec python3 view_reference_site.py
