@echo off
setlocal
cd /d "%~dp0"

if not exist package.json (
  echo [ERROR] package.json not found in project root.
  exit /b 1
)

if not exist node_modules (
  echo Installing desktop dependencies...
  call npm install
  if errorlevel 1 exit /b 1
)

echo Starting EGE Trainer Desktop (dev mode)...
call npm run desktop:dev
