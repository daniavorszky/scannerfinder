@echo off
rem Double-click this file on Windows to look at the built site in your browser.
rem It serves the dist folder exactly as it will be deployed. Close the window to stop it.
cd /d "%~dp0"
where npm >nul 2>nul
if errorlevel 1 (
  echo Node.js is not installed. Get it at nodejs.org, then open this file again.
  pause
  exit /b 1
)
if not exist node_modules call npm install --no-audit --no-fund
if not exist dist\index.html call npm run build
echo Serving the site. Your browser opens in a moment. Close this window to stop.
call npx astro preview --open
pause
