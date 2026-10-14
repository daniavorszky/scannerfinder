#!/bin/sh
# Double-click this file on a Mac to look at the built site in your browser.
# It serves the dist folder exactly as it will be deployed. Close the window to stop it.
cd "$(dirname "$0")" || exit 1
if ! command -v npm >/dev/null 2>&1; then
  echo "Node.js is not installed. Get it at nodejs.org, then open this file again."
  printf "Press Return to close. "; read _; exit 1
fi
[ -d node_modules ] || npm install --no-audit --no-fund || exit 1
[ -f dist/index.html ] || npm run build || exit 1
echo "Serving the site. Your browser opens in a moment. Close this window to stop."
if [ -n "$NO_OPEN" ]; then exec npx astro preview "$@"; fi
exec npx astro preview --open "$@"
