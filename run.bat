@echo off
REM One-click launcher (Windows). Creates a venv, installs deps, starts the dashboard.
cd /d "%~dp0"
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
echo Installing requirements...
pip install -r requirements.txt -q
echo Starting dashboard...
streamlit run app.py
pause
