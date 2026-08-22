@echo off
cd /d %~dp0
if not exist .venv\Scripts\python.exe (
  echo Please create a virtual environment first:
  echo   python -m venv .venv
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
