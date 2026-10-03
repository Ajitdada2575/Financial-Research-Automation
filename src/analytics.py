"""Clean, structure and analyse the scraped quarterly data (Pandas + NumPy)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

CORE_METRICS = ["Revenue", "Operating Profit", "Net Profit", "OPM %", "EPS"]


def clean(long_df: pd.DataFrame, n_quarters: int = config.DEFAULT_QUARTERS) -> pd.DataFrame:
    """Keep the latest n quarters, drop empty values, sort."""
    df = long_df.dropna(subset=["Value"]).copy()
    df["Quarter"] = pd.to_datetime(df["Quarter"])
    # cut-off = n-th latest quarter of each company
    cutoff = df.groupby("Company")["Quarter"].transform(
        lambda q: sorted(q.unique())[-n_quarters:][0])
    mask = df["Quarter"] >= cutoff
    return df[mask].sort_values(["Company", "Quarter", "Metric"]).reset_index(drop=True)


def to_wide(long_df: pd.DataFrame) -> pd.DataFrame:
    """One row per Company-Quarter, one column per metric + derived columns."""
    wide = long_df.pivot_table(index=["Company", "Quarter"], columns="Metric",
                               values="Value", aggfunc="first").reset_index()
    wide.columns.name = None
    wide = wide.sort_values(["Company", "Quarter"]).reset_index(drop=True)

    g = wide.groupby("Company")
    wide["Revenue QoQ %"] = g["Revenue"].pct_change() * 100
    wide["Revenue YoY %"] = g["Revenue"].pct_change(4) * 100
    wide["Net Profit QoQ %"] = g["Net Profit"].pct_change() * 100
    wide["Net Profit YoY %"] = g["Net Profit"].pct_change(4) * 100
    wide["Net Margin %"] = wide["Net Profit"] / wide["Revenue"] * 100
    wide["Revenue 4Q Avg"] = g["Revenue"].transform(lambda s: s.rolling(4, min_periods=1).mean())
    wide["Quarter Label"] = wide["Quarter"].dt.strftime("%b %Y")
    return wide.replace([np.inf, -np.inf], np.nan)


def latest_snapshot(wide: pd.DataFrame) -> pd.DataFrame:
    """Latest quarter per company with ranks (NumPy z-score for revenue growth)."""
    snap = wide.sort_values("Quarter").groupby("Company").tail(1).set_index("Company")
    cols = ["Quarter Label", "Revenue", "Operating Profit", "Net Profit", "OPM %",
            "Net Margin %", "EPS", "Revenue QoQ %", "Revenue YoY %", "Net Profit YoY %"]
    snap = snap[cols].copy()
    snap["Revenue Rank"] = snap["Revenue"].rank(ascending=False).astype(int)
    snap["Margin Rank"] = snap["OPM %"].rank(ascending=False).astype(int)
    yoy = snap["Revenue YoY %"].to_numpy(dtype=float)
    if np.isfinite(yoy).sum() > 1 and np.nanstd(yoy) > 0:
        snap["Growth Z-Score"] = (yoy - np.nanmean(yoy)) / np.nanstd(yoy)
    else:
        snap["Growth Z-Score"] = 0.0
    return snap.reset_index()


def cagr(series: pd.Series, periods_per_year: int = 4) -> float:
    s = series.dropna()
    if len(s) < 2 or s.iloc[0] <= 0:
        return float("nan")
    years = (len(s) - 1) / periods_per_year
    return float((s.iloc[-1] / s.iloc[0]) ** (1 / years) - 1) * 100


def company_insights(wide: pd.DataFrame, company: str) -> list[str]:
    """Plain-English insights for one company (used on PPT slides and dashboard)."""
    g = wide[wide["Company"] == company].sort_values("Quarter")
    if len(g) < 2:
        return ["Not enough history for insights."]
    last, prev = g.iloc[-1], g.iloc[-2]
    out = []

    rev_qoq = last["Revenue QoQ %"]
    if pd.notna(rev_qoq):
        word = "grew" if rev_qoq >= 0 else "declined"
        out.append(f"Revenue {word} {abs(rev_qoq):.1f}% QoQ to Rs {last['Revenue']:,.0f} Cr in {last['Quarter Label']}.")
    if pd.notna(last["Revenue YoY %"]):
        out.append(f"Year-on-year revenue growth stands at {last['Revenue YoY %']:.1f}%.")

    d_opm = last["OPM %"] - prev["OPM %"]
    trend = "expanded" if d_opm > 0 else "contracted"
    out.append(f"Operating margin {trend} by {abs(d_opm):.1f} pts to {last['OPM %']:.1f}%.")

    if pd.notna(last["Net Profit YoY %"]):
        out.append(f"Net profit of Rs {last['Net Profit']:,.0f} Cr is {last['Net Profit YoY %']:+.1f}% YoY.")

    c = cagr(g["Revenue"])
    if pd.notna(c):
        out.append(f"Annualised revenue growth (CAGR) over the window: {c:.1f}%.")

    # volatility with NumPy
    qoq = g["Revenue QoQ %"].dropna().to_numpy()
    if len(qoq) > 2:
        out.append(f"Revenue volatility (std-dev of QoQ growth): {np.std(qoq):.2f} pts.")
    return out


def sector_summary(wide: pd.DataFrame, snap: pd.DataFrame) -> list[str]:
    """Headline findings across all companies."""
    if snap.empty:
        return []
    lines = []
    top_rev = snap.sort_values("Revenue", ascending=False).iloc[0]
    lines.append(f"{top_rev['Company']} is the largest by quarterly revenue (Rs {top_rev['Revenue']:,.0f} Cr).")
    top_m = snap.sort_values("OPM %", ascending=False).iloc[0]
    lines.append(f"{top_m['Company']} leads on operating margin at {top_m['OPM %']:.1f}%.")
    g = snap.dropna(subset=["Revenue YoY %"])
    if not g.empty:
        top_g = g.sort_values("Revenue YoY %", ascending=False).iloc[0]
        lines.append(f"{top_g['Company']} shows the fastest YoY revenue growth ({top_g['Revenue YoY %']:.1f}%).")
        lines.append(f"Peer-average YoY revenue growth: {g['Revenue YoY %'].mean():.1f}%.")
    lines.append(f"Peer-average operating margin: {snap['OPM %'].mean():.1f}%.")
    return lines
