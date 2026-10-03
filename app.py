"""Streamlit dashboard - one-click financial research automation.

Run:  streamlit run app.py
"""
import logging

import pandas as pd
import streamlit as st

from src import analytics, config, pipeline
from src import ui_style as ui

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Financial Research Automation", page_icon="📊", layout="wide")
st.markdown(ui.CSS, unsafe_allow_html=True)


def _display(df: pd.DataFrame) -> pd.DataFrame:
    """Display-friendly copy: quarter as text, numbers rounded."""
    d = df.copy()
    if "Quarter" in d:
        d["Quarter"] = d["Quarter"].dt.strftime("%b %Y")
    num = d.select_dtypes("number").columns
    d[num] = d[num].round(2)
    return d


# ------------------------------- Sidebar -------------------------------- #
with st.sidebar:
    st.markdown('<div class="side-brand"><span class="logo">📊</span>FinResearch</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-note">Automated quarterly analysis of listed IT companies</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### ⚙️ Configure")
    source_label = st.radio(
        "Data source",
        ["Demo data (offline)", "Live scrape (Screener.in)", "Last cached scrape"],
        help="Demo data is synthetic and works without internet. Live scrape needs internet "
             "(and Chrome for Selenium; otherwise it falls back to requests).",
    )
    source = {"Demo data (offline)": "demo", "Live scrape (Screener.in)": "live",
              "Last cached scrape": "cache"}[source_label]

    companies = st.multiselect("Companies", list(config.COMPANIES), default=list(config.COMPANIES))
    n_quarters = st.slider("Quarters to analyse", 4, 12, config.DEFAULT_QUARTERS)
    method = "auto"
    if source == "live":
        method = st.selectbox("Fetch method", ["auto", "selenium", "requests"],
                              help="auto = try Selenium first, fall back to requests")
    st.markdown("&nbsp;", unsafe_allow_html=True)
    run_clicked = st.button("🚀  Run Full Analysis", type="primary", width="stretch")
    st.markdown("---")
    st.markdown(
        '<div class="side-note"><b>Stack</b><br>Python · Selenium · BeautifulSoup · Pandas · NumPy · '
        'Matplotlib · Streamlit · python-pptx</div>', unsafe_allow_html=True)

# --------------------------------- Hero --------------------------------- #
st.markdown(
    ui.hero("Financial Research Automation",
            "Scrape quarterly results, crunch the numbers, draw the charts and generate a "
            "presentation-ready PowerPoint, all in one click.",
            ["🌐 Selenium + BeautifulSoup", "🧮 Pandas + NumPy", "📈 Matplotlib", "📑 python-pptx", "⚡ One-click run"]),
    unsafe_allow_html=True)

# ------------------------------- Run ------------------------------------ #
if run_clicked:
    if len(companies) == 0:
        st.error("Select at least one company.")
    else:
        bar = st.progress(0.0, text="Starting…")

        def on_progress(frac, name):
            bar.progress(min(frac, 1.0), text=f"Scraped {name}")

        try:
            with st.spinner("Running pipeline: collect → clean → analyse → chart → report…"):
                st.session_state["result"] = pipeline.run(
                    companies, source, n_quarters, method, on_progress)
            bar.empty()
            st.toast("Analysis complete! Report is ready.", icon="✅")
        except Exception as exc:
            bar.empty()
            st.error(f"Pipeline failed: {exc}")
            if source == "live":
                st.info("Tip: switch to **Demo data** or try Fetch method = requests.")

res = st.session_state.get("result")

# ------------------------------ Welcome --------------------------------- #
if res is None:
    st.markdown(ui.section("How it works", "three steps"), unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(ui.step_card(1, "Choose", "Pick a data source, the companies and how many quarters to analyse in the sidebar."), unsafe_allow_html=True)
    c2.markdown(ui.step_card(2, "Run", "Click <b>Run Full Analysis</b>. The pipeline scrapes, cleans, analyses and charts automatically."), unsafe_allow_html=True)
    c3.markdown(ui.step_card(3, "Download", "Explore KPIs and insights, then download the PowerPoint report and Excel workbook."), unsafe_allow_html=True)

    st.markdown(ui.section("What you get"), unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    f1.markdown(ui.info_card("🏆", "Peer ranking", "Revenue, margin and growth ranks across all companies."), unsafe_allow_html=True)
    f2.markdown(ui.info_card("📊", "10 charts", "Trends, comparisons, heatmap and per-company dual-axis views."), unsafe_allow_html=True)
    f3.markdown(ui.info_card("💡", "Auto insights", "Plain-English takeaways generated from the numbers."), unsafe_allow_html=True)
    f4.markdown(ui.info_card("📑", "14-slide deck", "A ready-to-present PowerPoint built with python-pptx."), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 New here? Choose **Demo data (offline)** and click **Run Full Analysis** to see it work instantly.")
    st.markdown('<div class="footer">Built with Python · Selenium · BeautifulSoup · Pandas · NumPy · Matplotlib · Streamlit · python-pptx</div>', unsafe_allow_html=True)
    st.stop()

# ------------------------------ Results --------------------------------- #
for w in res.warnings:
    st.warning(w)

snap, wide = res.snapshot, res.wide
latest_q = snap["Quarter Label"].iloc[0]

st.markdown(
    f'{ui.source_pill(res.source_label)} &nbsp; <span style="color:#7A8A9B;font-size:.88rem">'
    f'{res.source_label} · latest quarter <b>{latest_q}</b> · {len(snap)} companies · '
    f'{wide["Quarter"].nunique()} quarters</span>', unsafe_allow_html=True)
if "Demo" in res.source_label:
    st.warning("Showing **synthetic demo data**, not real financials. Use *Live scrape* for real numbers.")

top = snap.sort_values("Revenue", ascending=False).iloc[0]
best_m = snap.sort_values("OPM %", ascending=False).iloc[0]
g = snap.dropna(subset=["Revenue YoY %"])
fast = g.sort_values("Revenue YoY %", ascending=False).iloc[0] if not g.empty else None

st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k1.markdown(ui.kpi("k1", "Largest revenue", top["Company"], f"Rs {top['Revenue']:,.0f} Cr"), unsafe_allow_html=True)
k2.markdown(ui.kpi("k2", "Best operating margin", best_m["Company"], f"{best_m['OPM %']:.1f}% OPM"), unsafe_allow_html=True)
k3.markdown(ui.kpi("k3", "Fastest growth (YoY)", fast["Company"] if fast is not None else "-",
                   f"{fast['Revenue YoY %']:.1f}% revenue" if fast is not None else ""), unsafe_allow_html=True)
k4.markdown(ui.kpi("k4", "Peer avg revenue YoY", f"{g['Revenue YoY %'].mean():.1f}%" if not g.empty else "-",
                   f"across {len(snap)} companies"), unsafe_allow_html=True)

# Leaderboard
st.markdown(ui.section("Leaderboard", "ranked by latest quarterly revenue"), unsafe_allow_html=True)
ranked = snap.sort_values("Revenue", ascending=False).reset_index(drop=True)
max_rev = ranked["Revenue"].max()
cols = st.columns(len(ranked))
for i, col in enumerate(cols, start=1):
    row = ranked.iloc[i - 1]
    col.markdown(ui.rank_card(i, row["Company"], row["Revenue"], row["Quarter Label"], row["OPM %"],
                              row["Revenue"] / max_rev * 100, row["Revenue YoY %"]), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------- Tabs ----------------------------------- #
tab_over, tab_charts, tab_company, tab_data, tab_dl = st.tabs(
    ["🏠 Overview", "📊 Charts", "🏢 Company view", "🗂️ Data", "⬇️ Downloads"])

with tab_over:
    left, right = st.columns([2, 3], gap="large")
    with left:
        st.markdown(ui.section("Key takeaways"), unsafe_allow_html=True)
        for i, line in enumerate(analytics.sector_summary(wide, snap)):
            st.markdown(ui.insight(line, alt=i % 2 == 1), unsafe_allow_html=True)
    with right:
        st.markdown(ui.section("Latest quarter snapshot"), unsafe_allow_html=True)
        show = snap[["Company", "Quarter Label", "Revenue", "Net Profit", "OPM %", "Revenue YoY %",
                     "Net Profit YoY %", "EPS"]].rename(columns={"Quarter Label": "Quarter"})
        st.dataframe(
            show, width="stretch", hide_index=True,
            column_config={
                "Revenue": st.column_config.NumberColumn("Revenue (Rs Cr)", format="localized"),
                "Net Profit": st.column_config.NumberColumn("Net Profit (Rs Cr)", format="localized"),
                "OPM %": st.column_config.ProgressColumn("OPM %", format="%.1f%%", min_value=0,
                                                         max_value=float(max(40, show["OPM %"].max()))),
                "Revenue YoY %": st.column_config.NumberColumn("Rev YoY", format="%.1f%%"),
                "Net Profit YoY %": st.column_config.NumberColumn("Profit YoY", format="%.1f%%"),
                "EPS": st.column_config.NumberColumn("EPS (Rs)", format="%.2f"),
            })
    st.markdown(ui.section("Revenue vs margin at a glance"), unsafe_allow_html=True)
    a, b = st.columns(2, gap="large")
    with a, st.container(border=True):
        st.image(str(res.charts["Revenue trend"]), width="stretch")
    with b, st.container(border=True):
        st.image(str(res.charts["Net profit (latest)"]), width="stretch")

with tab_charts:
    keys = [k for k in res.charts if not k.startswith("company::")]
    for i in range(0, len(keys), 2):
        cols = st.columns(2, gap="large")
        for col, k in zip(cols, keys[i:i + 2]):
            with col, st.container(border=True):
                st.markdown(f"**{k}**")
                st.image(str(res.charts[k]), width="stretch")

with tab_company:
    comp = st.selectbox("Select company", sorted(wide["Company"].unique()))
    row = snap[snap["Company"] == comp].iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(ui.kpi("k1", "Revenue", f"Rs {row['Revenue']:,.0f} Cr", row["Quarter Label"]), unsafe_allow_html=True)
    m2.markdown(ui.kpi("k2", "Net profit", f"Rs {row['Net Profit']:,.0f} Cr", f"Net margin {row['Net Margin %']:.1f}%"), unsafe_allow_html=True)
    m3.markdown(ui.kpi("k3", "Operating margin", f"{row['OPM %']:.1f}%", f"Rank #{int(row['Margin Rank'])} of {len(snap)}"), unsafe_allow_html=True)
    yoy = row["Revenue YoY %"]
    m4.markdown(ui.kpi("k4", "Revenue YoY", "-" if pd.isna(yoy) else f"{yoy:+.1f}%", f"Revenue rank #{int(row['Revenue Rank'])}"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([3, 2], gap="large")
    with left, st.container(border=True):
        st.image(str(res.charts[f"company::{comp}"]), width="stretch")
    with right:
        st.markdown(ui.section("Insights"), unsafe_allow_html=True)
        for i, line in enumerate(analytics.company_insights(wide, comp)):
            st.markdown(ui.insight(line, alt=i % 2 == 1), unsafe_allow_html=True)
    st.markdown(ui.section("Quarterly history"), unsafe_allow_html=True)
    st.dataframe(_display(wide[wide["Company"] == comp].drop(columns=["Quarter Label"])),
                 width="stretch", hide_index=True)

with tab_data:
    st.markdown(ui.section("Quarterly data", "all companies, all derived metrics"), unsafe_allow_html=True)
    st.dataframe(_display(wide.drop(columns=["Quarter Label"])), width="stretch", hide_index=True)
    st.download_button("⬇️ Download CSV", wide.to_csv(index=False).encode(), "financials_wide.csv", "text/csv")

with tab_dl:
    st.markdown(ui.section("Your generated files"), unsafe_allow_html=True)
    d1, d2 = st.columns(2, gap="large")
    with d1:
        st.markdown(ui.info_card("📑", "PowerPoint report",
                    "14 slides: takeaways, snapshot table, charts and a deep-dive for every company."), unsafe_allow_html=True)
        with open(res.pptx_path, "rb") as f:
            st.download_button("⬇️ Download PPTX", f.read(), res.pptx_path.name,
                               "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                               type="primary", key="dl_pptx")
    with d2:
        st.markdown(ui.info_card("📗", "Excel workbook",
                    "Three sheets: latest snapshot, quarterly analytics and the raw long-format data."), unsafe_allow_html=True)
        with open(res.excel_path, "rb") as f:
            st.download_button("⬇️ Download XLSX", f.read(), res.excel_path.name,
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_xlsx")
    st.caption(f"Also saved on disk: {res.pptx_path}")

st.markdown('<div class="footer">Financial Research Automation · Python · Selenium · BeautifulSoup · Pandas · NumPy · Matplotlib · Streamlit · python-pptx<br>For information only, not investment advice.</div>', unsafe_allow_html=True)
