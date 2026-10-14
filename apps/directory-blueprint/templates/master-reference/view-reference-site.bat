@echo off
rem Double-click this file on Windows to look at the reference site in your browser.
rem It serves the site folder beside it from your own computer. Close the window to stop it.
cd /d "%~dp0"
if not exist view_reference_site.py (
  echo Unzip the Blueprint first, then open this file from the unzipped folder.
  pause
  exit /b 1
)
rem py is the python.org launcher; "python" alone can be the Microsoft Store stub, so test that it really runs.
py -3 --version >nul 2>nul
if not errorlevel 1 (
  py -3 view_reference_site.py
  goto done
)
python --version >nul 2>nul
if not errorlevel 1 (
  python view_reference_site.py
  goto done
)
echo Python 3 is not installed. Get it at python.org, then open this file again.
:done
pause
