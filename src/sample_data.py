"""Offline DEMO data so the project runs without internet / Chrome.

IMPORTANT: these numbers are synthetic and only *roughly* in the range of real
quarterly figures. They exist to demonstrate the pipeline. Use "Live scrape"
for real data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# base quarterly revenue (Rs Cr), operating margin %, net margin %, qoq drift, shares (Cr)
_PROFILE = {
    "TCS":           (61000, 24.5, 19.0, 0.012, 362),
    "Infosys":       (39500, 21.0, 16.0, 0.010, 415),
    "Wipro":         (22300, 17.5, 14.0, 0.004, 1045),
    "HCLTech":       (28500, 19.5, 14.5, 0.011, 271),
    "Tech Mahindra": (13100, 11.0,  8.0, 0.009, 97),
}


def _quarter_ends(n: int) -> list[pd.Timestamp]:
    end = pd.Timestamp("2026-06-01")  # latest quarter = Jun 2026
    return list(pd.date_range(end=end, periods=n, freq="3MS"))


def generate(companies: list[str], n_quarters: int = 8, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    quarters = _quarter_ends(n_quarters)
    rows = []
    for name in companies:
        base, opm, npm, drift, shares = _PROFILE.get(name, (15000, 15.0, 11.0, 0.008, 100))
        rev = base * (1 + drift) ** np.arange(-n_quarters + 1, 1)
        rev = rev * (1 + rng.normal(0, 0.012, n_quarters))
        opm_series = np.clip(opm + rng.normal(0, 0.6, n_quarters), 5, 35)
        npm_series = np.clip(npm + rng.normal(0, 0.5, n_quarters), 3, 30)
        op_profit = rev * opm_series / 100
        expenses = rev - op_profit
        other_inc = rev * rng.uniform(0.012, 0.025, n_quarters)
        interest = rev * rng.uniform(0.002, 0.006, n_quarters)
        dep = rev * rng.uniform(0.020, 0.032, n_quarters)
        net = rev * npm_series / 100
        tax_pct = np.clip(rng.normal(25.5, 0.8, n_quarters), 22, 29)
        pbt = net / (1 - tax_pct / 100)
        eps = net / shares
        metrics = {
            "Revenue": rev, "Expenses": expenses, "Operating Profit": op_profit,
            "OPM %": opm_series, "Other Income": other_inc, "Interest": interest,
            "Depreciation": dep, "PBT": pbt, "Tax %": tax_pct,
            "Net Profit": net, "EPS": eps,
        }
        for metric, vals in metrics.items():
            for q, v in zip(quarters, vals):
                rows.append({"Company": name, "Quarter": q, "Metric": metric,
                             "Value": round(float(v), 2)})
    return pd.DataFrame(rows)
