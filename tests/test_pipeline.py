"""Run with:  python -m pytest -q   (or just: python tests/test_pipeline.py)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import analytics, pipeline, sample_data, scraper

# Minimal HTML mimicking the structure of Screener.in's quarterly-results table.
FIXTURE = """
<section id="quarters"><table class="data-table"><thead><tr>
<th></th><th>Mar 2025</th><th>Jun 2025</th><th>Sep 2025</th></tr></thead><tbody>
<tr><td class="text">Sales&nbsp;+</td><td>1,000</td><td>1,100</td><td>1,210</td></tr>
<tr><td class="text">Expenses&nbsp;+</td><td>800</td><td>870</td><td>950</td></tr>
<tr><td class="text">Operating Profit</td><td>200</td><td>230</td><td>260</td></tr>
<tr><td class="text">OPM %</td><td>20%</td><td>21%</td><td>21%</td></tr>
<tr><td class="text">Net Profit&nbsp;+</td><td>150</td><td>170</td><td>190</td></tr>
<tr><td class="text">EPS in Rs</td><td>15.0</td><td>17.0</td><td>19.0</td></tr>
</tbody></table></section>
"""


def test_parser():
    df = scraper.parse_quarterly_table(FIXTURE, "DemoCo")
    rev = df[(df.Metric == "Revenue")].sort_values("Quarter")["Value"].tolist()
    assert rev == [1000.0, 1100.0, 1210.0]
    assert set(df.Metric) >= {"Revenue", "Net Profit", "OPM %", "EPS"}


def test_analytics():
    long_df = scraper.parse_quarterly_table(FIXTURE, "DemoCo")
    wide = analytics.to_wide(analytics.clean(long_df, 8))
    assert round(wide["Revenue QoQ %"].iloc[-1], 1) == 10.0


def test_full_demo_pipeline():
    res = pipeline.run(["TCS", "Infosys"], "demo", 6)
    assert res.pptx_path.exists() and res.excel_path.exists()
    assert len(res.snapshot) == 2


if __name__ == "__main__":
    test_parser(); test_analytics(); test_full_demo_pipeline()
    print("All tests passed")
