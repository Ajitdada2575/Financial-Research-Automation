"""Matplotlib chart generation. Every function saves a PNG and returns its path."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend: works inside Streamlit and servers
import logging
logging.getLogger("matplotlib.category").setLevel(logging.WARNING)
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd

from . import config

plt.rcParams.update({
    "font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "axes.titleweight": "bold", "axes.titlesize": 13,
})


def _color(i: int) -> str:
    return config.PALETTE[i % len(config.PALETTE)]


def _save(fig, name: str) -> Path:
    path = config.CHART_DIR / f"{name}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def revenue_trend(wide: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (comp, g) in enumerate(wide.groupby("Company")):
        ax.plot(g["Quarter Label"], g["Revenue"], marker="o", lw=2.2, color=_color(i), label=comp)
    ax.set_title("Quarterly Revenue Trend (Rs Crore)")
    ax.set_ylabel("Revenue (Rs Cr)")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.legend(frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, "revenue_trend")


def margin_trend(wide: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (comp, g) in enumerate(wide.groupby("Company")):
        ax.plot(g["Quarter Label"], g["OPM %"], marker="s", lw=2.2, color=_color(i), label=comp)
    ax.set_title("Operating Profit Margin (%)")
    ax.set_ylabel("OPM %")
    ax.legend(frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, "margin_trend")


def net_profit_latest(snap: pd.DataFrame) -> Path:
    s = snap.sort_values("Net Profit", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(s["Company"], s["Net Profit"], color=[_color(i) for i in range(len(s))])
    for b, v in zip(bars, s["Net Profit"]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
    ax.set_title(f"Net Profit - Latest Quarter ({s['Quarter Label'].iloc[0]})")
    ax.set_ylabel("Net Profit (Rs Cr)")
    ax.grid(axis="x", visible=False)
    return _save(fig, "net_profit_latest")


def growth_comparison(snap: pd.DataFrame) -> Path:
    s = snap.sort_values("Company")
    x = np.arange(len(s))
    w = 0.38
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - w / 2, s["Revenue YoY %"], w, label="Revenue YoY %", color=config.PALETTE[0])
    ax.bar(x + w / 2, s["Net Profit YoY %"], w, label="Net Profit YoY %", color=config.PALETTE[2])
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(s["Company"])
    ax.set_title("Year-on-Year Growth (Latest Quarter)")
    ax.set_ylabel("%")
    ax.legend(frameon=False)
    ax.grid(axis="x", visible=False)
    return _save(fig, "growth_comparison")


def yoy_heatmap(wide: pd.DataFrame) -> Path:
    pv = wide.pivot(index="Company", columns="Quarter Label", values="Revenue QoQ %")
    order = wide.drop_duplicates("Quarter Label").sort_values("Quarter")["Quarter Label"]
    pv = pv[list(order)]
    fig, ax = plt.subplots(figsize=(11, 4.6))
    vals = pv.to_numpy(dtype=float)
    lim = np.nanmax(np.abs(vals)) if np.isfinite(vals).any() else 1
    im = ax.imshow(vals, cmap="RdYlGn", vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(pv.shape[1]))
    ax.set_xticklabels(pv.columns, rotation=30, ha="right")
    ax.set_yticks(range(pv.shape[0]))
    ax.set_yticklabels(pv.index)
    ax.grid(False)
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            if np.isfinite(vals[i, j]):
                ax.text(j, i, f"{vals[i, j]:.1f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="QoQ revenue growth %")
    ax.set_title("QoQ Revenue Growth Heatmap")
    return _save(fig, "qoq_heatmap")


def company_chart(wide: pd.DataFrame, company: str, idx: int = 0) -> Path:
    g = wide[wide["Company"] == company].sort_values("Quarter")
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    x = np.arange(len(g))
    w = 0.38
    ax.bar(x - w / 2, g["Revenue"], w, color=_color(idx), label="Revenue")
    ax.bar(x + w / 2, g["Net Profit"], w, color=config.PALETTE[2], label="Net Profit")
    ax.set_xticks(x)
    ax.set_xticklabels(g["Quarter Label"], rotation=30, ha="right")
    ax.set_ylabel("Rs Crore")
    ax.set_ylim(0, g["Revenue"].max() * 1.3)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.grid(axis="x", visible=False)
    ax2 = ax.twinx()
    ax2.plot(x, g["OPM %"], color=config.PALETTE[3], marker="o", lw=2, label="OPM %")
    ax2.set_ylabel("OPM %")
    ax2.set_ylim(max(0, g["OPM %"].min() - 4), g["OPM %"].max() + 4)
    ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, loc="upper left", ncol=3, fontsize=9)
    ax.set_title(f"{company}: Revenue, Net Profit & Margin")
    return _save(fig, f"company_{company.replace(' ', '_')}")


def build_all(wide: pd.DataFrame, snap: pd.DataFrame) -> dict[str, Path]:
    charts = {
        "Revenue trend": revenue_trend(wide),
        "Margin trend": margin_trend(wide),
        "Net profit (latest)": net_profit_latest(snap),
        "Growth comparison": growth_comparison(snap),
        "QoQ heatmap": yoy_heatmap(wide),
    }
    for i, comp in enumerate(sorted(wide["Company"].unique())):
        charts[f"company::{comp}"] = company_chart(wide, comp, i)
    return charts
