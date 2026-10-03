#!/usr/bin/env bash
# One-click launcher (macOS / Linux).
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -q
streamlit run app.py
