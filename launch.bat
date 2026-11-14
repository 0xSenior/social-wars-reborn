@echo off
title Social Wars: Reborn Launcher
cd /d "%~dp0"
echo Starting Social Wars: Reborn Desktop Edition...
node_modules\electron\dist\electron.exe .
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to launch Electron.
    pause
)
