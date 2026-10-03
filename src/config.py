"""Central configuration for the Financial Research Automation project."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHART_DIR = BASE_DIR / "outputs" / "charts"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

for _d in (RAW_DIR, PROCESSED_DIR, CHART_DIR, REPORT_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Publicly listed Indian IT companies -> Screener.in slug
COMPANIES = {
    "TCS": "TCS",
    "Infosys": "INFY",
    "Wipro": "WIPRO",
    "HCLTech": "HCLTECH",
    "Tech Mahindra": "TECHM",
}

SCREENER_URL = "https://www.screener.in/company/{slug}/consolidated/"

# Row label on the quarterly-results table -> clean metric name (Rs. Crore unless noted)
METRIC_MAP = {
    "sales": "Revenue",
    "expenses": "Expenses",
    "operating profit": "Operating Profit",
    "opm %": "OPM %",
    "other income": "Other Income",
    "interest": "Interest",
    "depreciation": "Depreciation",
    "profit before tax": "PBT",
    "tax %": "Tax %",
    "net profit": "Net Profit",
    "eps in rs": "EPS",
}

DEFAULT_QUARTERS = 8
REQUEST_TIMEOUT = 20
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

PALETTE = ["#1F4E79", "#2E86AB", "#F18F01", "#C73E1D", "#3B8B5A", "#6C4F9E"]
