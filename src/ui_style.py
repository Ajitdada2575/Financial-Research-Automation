"""Look & feel for the Streamlit dashboard: CSS + small HTML component helpers."""
from __future__ import annotations

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, button, input { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1280px;}

/* ---------- Hero ---------- */
.hero {
  background: linear-gradient(120deg, #0F2D4A 0%, #1F4E79 45%, #2E86AB 100%);
  border-radius: 22px; padding: 34px 40px; color: #fff; position: relative; overflow: hidden;
  box-shadow: 0 14px 40px rgba(31,78,121,.28); margin-bottom: 22px;
}
.hero:before {content:""; position:absolute; right:-80px; top:-90px; width:320px; height:320px;
  background: radial-gradient(circle, rgba(241,143,1,.55), rgba(241,143,1,0) 70%);}
.hero:after {content:""; position:absolute; right:140px; bottom:-120px; width:260px; height:260px;
  background: radial-gradient(circle, rgba(255,255,255,.18), rgba(255,255,255,0) 70%);}
.hero h1 {margin:0; font-size: 2.35rem; font-weight: 800; letter-spacing:-.5px; color:#fff;}
.hero p {margin: 8px 0 18px; font-size: 1.05rem; opacity:.9; max-width: 720px;}
.chip {display:inline-block; padding:5px 13px; margin:0 8px 8px 0; border-radius:999px; font-size:.78rem;
  font-weight:600; background: rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.28);}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {background: linear-gradient(180deg,#0F2D4A 0%,#173f63 100%);}
section[data-testid="stSidebar"] * {color:#E8F0F8;}
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {color:#fff !important;}
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="input"] {background: rgba(255,255,255,.10); border-color: rgba(255,255,255,.25);}
section[data-testid="stSidebar"] [data-baseweb="tag"] {background:#F18F01 !important;}
section[data-testid="stSidebar"] [data-baseweb="tag"] * {color:#fff !important;}
section[data-testid="stSidebar"] hr {border-color: rgba(255,255,255,.18);}
.side-brand {display:flex; align-items:center; gap:10px; font-weight:800; font-size:1.15rem; margin-bottom:6px;}
.side-brand span.logo {background:#F18F01; width:36px; height:36px; border-radius:10px; display:flex;
  align-items:center; justify-content:center; font-size:1.2rem;}
.side-note {font-size:.75rem; opacity:.7; line-height:1.5;}

/* ---------- Buttons ---------- */
button[kind="primary"], [data-testid="stBaseButton-primary"] {
  background: linear-gradient(90deg,#F18F01,#F5A83A) !important; color:#fff !important; border:none !important;
  font-weight:700 !important; border-radius:12px !important; padding:.65rem 1rem !important;
  box-shadow: 0 8px 20px rgba(241,143,1,.38); transition: transform .15s, box-shadow .15s;}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {transform: translateY(-2px);
  box-shadow: 0 12px 26px rgba(241,143,1,.5);}
[data-testid="stDownloadButton"] button {border-radius:12px; font-weight:600; width:100%;}

/* ---------- Cards ---------- */
.card {background:#fff; border-radius:18px; padding:20px 22px; box-shadow: 0 6px 24px rgba(20,50,90,.08);
  border:1px solid #E6EDF5; height:100%;}
.card h4 {margin:0 0 6px; color:#1F4E79; font-size:1.02rem; font-weight:700;}
.card p {margin:0; color:#5A6B7D; font-size:.9rem; line-height:1.5;}
.step-num {width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#1F4E79,#2E86AB); color:#fff;
  display:flex; align-items:center; justify-content:center; font-weight:800; margin-bottom:12px;}
.feat-icon {font-size:1.6rem; margin-bottom:8px;}

.kpi {border-radius:18px; padding:18px 20px; color:#fff; box-shadow: 0 10px 26px rgba(20,50,90,.18); height:100%;}
.kpi .lab {font-size:.78rem; text-transform:uppercase; letter-spacing:.8px; opacity:.85; font-weight:600;}
.kpi .val {font-size:1.7rem; font-weight:800; margin:4px 0 2px; line-height:1.15;}
.kpi .sub {font-size:.85rem; opacity:.9;}
.k1 {background:linear-gradient(135deg,#1F4E79,#2E86AB);}
.k2 {background:linear-gradient(135deg,#F18F01,#F7B955);}
.k3 {background:linear-gradient(135deg,#3B8B5A,#62B883);}
.k4 {background:linear-gradient(135deg,#6C4F9E,#9378C7);}

.rank-card {background:#fff; border-radius:16px; padding:16px 18px; border:1px solid #E6EDF5;
  box-shadow: 0 6px 20px rgba(20,50,90,.07); position:relative; overflow:hidden; height:100%;}
.rank-card .badge {position:absolute; right:12px; top:10px; font-size:.72rem; font-weight:800; color:#fff;
  background:#1F4E79; padding:3px 10px; border-radius:999px;}
.rank-card.gold .badge {background:#F18F01;}
.rank-card .name {font-weight:800; font-size:1.05rem; color:#1B2A3A; margin-bottom:2px;}
.rank-card .rev {font-size:1.35rem; font-weight:800; color:#1F4E79;}
.rank-card .meta {font-size:.78rem; color:#7A8A9B;}
.bar {height:7px; border-radius:99px; background:#E9EFF6; margin:10px 0 6px; overflow:hidden;}
.bar > div {height:100%; background:linear-gradient(90deg,#2E86AB,#1F4E79); border-radius:99px;}
.yoy {display:inline-block; padding:2px 10px; border-radius:999px; font-size:.78rem; font-weight:700;}
.yoy.pos {background:#E2F5EA; color:#1E7A45;}
.yoy.neg {background:#FCE6E3; color:#B3321F;}

.pill {display:inline-block; padding:5px 14px; border-radius:999px; font-size:.78rem; font-weight:700; letter-spacing:.4px;}
.pill.demo {background:#FFF1DA; color:#B86E00; border:1px solid #F7C77A;}
.pill.live {background:#E2F5EA; color:#1E7A45; border:1px solid #9AD8B3;}
.pill.cache {background:#E6EEF8; color:#1F4E79; border:1px solid #B5CBE6;}

.insight {background:#fff; border-left:5px solid #2E86AB; border-radius:10px; padding:11px 15px; margin-bottom:10px;
  box-shadow: 0 3px 12px rgba(20,50,90,.06); font-size:.92rem; color:#2A3A4C;}
.insight.alt {border-left-color:#F18F01;}
.sec-title {font-size:1.25rem; font-weight:800; color:#1B2A3A; margin:22px 0 12px;}
.sec-title small {font-weight:500; color:#7A8A9B; font-size:.85rem; margin-left:8px;}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {gap:8px; background:#fff; padding:6px; border-radius:14px; border:1px solid #E6EDF5;
  box-shadow:0 4px 14px rgba(20,50,90,.06);}
.stTabs [data-baseweb="tab"] {border-radius:10px; padding:8px 18px; font-weight:600; color:#5A6B7D; height:auto;}
.stTabs [aria-selected="true"] {background: linear-gradient(90deg,#1F4E79,#2E86AB); color:#fff !important;}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {display:none;}

[data-testid="stVerticalBlockBorderWrapper"] {border-radius:18px;}
[data-testid="stImage"] img {border-radius:12px;}
[data-testid="stDataFrame"] {border-radius:14px; overflow:hidden; box-shadow:0 4px 16px rgba(20,50,90,.07);}
.footer {text-align:center; color:#8B9AAB; font-size:.8rem; margin-top:40px; padding-top:18px; border-top:1px solid #E1E8F0;}
</style>
"""


def hero(title: str, subtitle: str, chips: list[str]) -> str:
    c = "".join(f'<span class="chip">{x}</span>' for x in chips)
    return f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p>{c}</div>'


def info_card(icon: str, title: str, text: str) -> str:
    return f'<div class="card"><div class="feat-icon">{icon}</div><h4>{title}</h4><p>{text}</p></div>'


def step_card(n: int, title: str, text: str) -> str:
    return f'<div class="card"><div class="step-num">{n}</div><h4>{title}</h4><p>{text}</p></div>'


def kpi(css: str, label: str, value: str, sub: str = "") -> str:
    return f'<div class="kpi {css}"><div class="lab">{label}</div><div class="val">{value}</div><div class="sub">{sub}</div></div>'


def rank_card(rank: int, name: str, revenue: float, quarter: str, opm: float, share: float, yoy) -> str:
    gold = " gold" if rank == 1 else ""
    if yoy is None or yoy != yoy:
        chip = '<span class="yoy pos">YoY n/a</span>'
    else:
        cls = "pos" if yoy >= 0 else "neg"
        arrow = "▲" if yoy >= 0 else "▼"
        chip = f'<span class="yoy {cls}">{arrow} {abs(yoy):.1f}% YoY</span>'
    return (f'<div class="rank-card{gold}"><span class="badge">#{rank}</span>'
            f'<div class="name">{name}</div><div class="rev">Rs {revenue:,.0f} Cr</div>'
            f'<div class="meta">Revenue · {quarter}</div>'
            f'<div class="bar"><div style="width:{share:.0f}%"></div></div>'
            f'<div class="meta">OPM {opm:.1f}% &nbsp; {chip}</div></div>')


def source_pill(label: str) -> str:
    kind = "demo" if "Demo" in label else ("cache" if "cached" in label else "live")
    text = {"demo": "DEMO DATA", "live": "LIVE DATA", "cache": "CACHED DATA"}[kind]
    return f'<span class="pill {kind}">● {text}</span>'


def insight(text: str, alt: bool = False) -> str:
    return f'<div class="insight{" alt" if alt else ""}">{text}</div>'


def section(title: str, sub: str = "") -> str:
    s = f"<small>{sub}</small>" if sub else ""
    return f'<div class="sec-title">{title}{s}</div>'
