"""End-to-end orchestration: collect -> clean -> analyse -> chart -> PPT."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import analytics, charts, config, ppt_builder, sample_data, scraper

log = logging.getLogger(__name__)

SOURCES = ("live", "demo", "cache")
CACHE_FILE = config.PROCESSED_DIR / "last_scrape_long.csv"


@dataclass
class PipelineResult:
    long_df: pd.DataFrame
    wide: pd.DataFrame
    snapshot: pd.DataFrame
    charts: dict
    pptx_path: Path
    excel_path: Path
    source_label: str
    warnings: list = field(default_factory=list)


def collect(companies: list[str], source: str, method: str = "auto", progress=None):
    warnings: list[str] = []
    if source == "live":
        df = scraper.scrape_all(companies, method, progress)
        df.to_csv(CACHE_FILE, index=False)
        warnings += [f"Could not scrape: {', '.join(df.attrs.get('failed', []))}"] \
            if df.attrs.get("failed") else []
        return df, "Screener.in (live)", warnings
    if source == "cache":
        if not CACHE_FILE.exists():
            raise FileNotFoundError("No cached scrape found. Run a live scrape first.")
        df = pd.read_csv(CACHE_FILE, parse_dates=["Quarter"])
        return df[df["Company"].isin(companies)], "Screener.in (cached)", warnings
    df = sample_data.generate(companies)
    return df, "Demo data (synthetic)", warnings


def run(companies: list[str], source: str = "demo", n_quarters: int = config.DEFAULT_QUARTERS,
        method: str = "auto", progress=None) -> PipelineResult:
    raw, label, warnings = collect(companies, source, method, progress)
    long_df = analytics.clean(raw, n_quarters)
    wide = analytics.to_wide(long_df)
    snap = analytics.latest_snapshot(wide)

    wide.to_csv(config.PROCESSED_DIR / "financials_wide.csv", index=False)
    excel_path = config.PROCESSED_DIR / "financial_analysis.xlsx"
    with pd.ExcelWriter(excel_path) as xw:
        snap.to_excel(xw, sheet_name="Latest Snapshot", index=False)
        wide.drop(columns=["Quarter Label"]).to_excel(xw, sheet_name="Quarterly Data", index=False)
        long_df.to_excel(xw, sheet_name="Raw Long Format", index=False)

    chart_paths = charts.build_all(wide, snap)
    pptx_path = ppt_builder.build_report(wide, snap, chart_paths, label)
    return PipelineResult(long_df, wide, snap, chart_paths, pptx_path, excel_path, label, warnings)
