@echo off
cd /d "%~dp0"
start "The Money Daemon" cmd /k ".venv\Scripts\python.exe -m daemon.src.main"
