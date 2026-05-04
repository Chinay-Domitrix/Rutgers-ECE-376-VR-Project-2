@echo off
setlocal

set "PORT=%~1"
if "%PORT%"=="" set "PORT=5173"
set "ROOT=%~dp0"
set "URL=http://localhost:%PORT%/"

echo Serving Rover Ready from "%ROOT%"
echo Opening %URL%
start "" "%URL%"

cd /d "%ROOT%"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m http.server %PORT%
    goto :eof
)

where python >nul 2>nul
if not errorlevel 1 (
    python -m http.server %PORT%
    goto :eof
)

where python3 >nul 2>nul
if not errorlevel 1 (
    python3 -m http.server %PORT%
    goto :eof
)

echo Python was not found on PATH.
echo Install Python or run this from another shell: python -m http.server %PORT%
exit /b 1
