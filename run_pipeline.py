"""Command-line entry point.

Examples:
    python run_pipeline.py                      # demo data, all companies
    python run_pipeline.py --source live        # scrape Screener.in
    python run_pipeline.py --source live --method requests --quarters 12
"""
import argparse
import logging

from src import config, pipeline

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

ap = argparse.ArgumentParser(description="Financial Research Automation")
ap.add_argument("--source", choices=pipeline.SOURCES, default="demo")
ap.add_argument("--method", choices=["auto", "selenium", "requests"], default="auto")
ap.add_argument("--quarters", type=int, default=config.DEFAULT_QUARTERS)
ap.add_argument("--companies", nargs="*", default=list(config.COMPANIES))
args = ap.parse_args()

res = pipeline.run(args.companies, args.source, args.quarters, args.method)
print("\nDone.")
print("PowerPoint :", res.pptx_path)
print("Excel      :", res.excel_path)
print("Charts     :", config.CHART_DIR)
print(res.snapshot[["Company", "Revenue", "Net Profit", "OPM %", "Revenue YoY %"]].round(1).to_string(index=False))
