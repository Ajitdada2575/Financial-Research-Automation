"""Scrape quarterly results of listed IT companies from Screener.in.

Flow: fetch HTML (Selenium headless Chrome -> falls back to requests)
      -> parse the "Quarterly Results" table with BeautifulSoup
      -> return a tidy long-format DataFrame.
"""
from __future__ import annotations

import logging
import re
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from . import config

log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Fetching HTML
# --------------------------------------------------------------------------- #
def fetch_html_selenium(url: str, wait: float = 2.0) -> str:
    """Load a page in headless Chrome and return the rendered HTML."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"--user-agent={config.USER_AGENT}")

    # Selenium >= 4.6 downloads a matching chromedriver automatically.
    driver = webdriver.Chrome(options=opts)
    try:
        driver.set_page_load_timeout(config.REQUEST_TIMEOUT * 2)
        driver.get(url)
        WebDriverWait(driver, config.REQUEST_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section#quarters table"))
        )
        time.sleep(wait)
        return driver.page_source
    finally:
        driver.quit()


def fetch_html_requests(url: str) -> str:
    """Plain HTTP fallback (the quarterly table is server-rendered)."""
    resp = requests.get(
        url, headers={"User-Agent": config.USER_AGENT}, timeout=config.REQUEST_TIMEOUT
    )
    resp.raise_for_status()
    return resp.text


def fetch_html(url: str, method: str = "auto") -> str:
    """method: 'selenium' | 'requests' | 'auto' (selenium, then requests)."""
    if method == "requests":
        return fetch_html_requests(url)
    if method == "selenium":
        return fetch_html_selenium(url)
    try:
        return fetch_html_selenium(url)
    except Exception as exc:  # no Chrome installed, driver download blocked, etc.
        log.warning("Selenium failed (%s). Falling back to requests.", exc)
        return fetch_html_requests(url)


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def _to_number(text: str) -> float | None:
    t = re.sub(r"[,%\s₹]", "", text or "")
    if t in ("", "-", "—"):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _clean_label(text: str) -> str:
    # "Sales +" -> "sales", "EPS in Rs" -> "eps in rs"
    return re.sub(r"[\s+\xa0]+$", "", text.replace("\xa0", " ")).strip().lower().rstrip("+").strip()


def parse_quarterly_table(html: str, company: str) -> pd.DataFrame:
    """Return long DataFrame: Company | Quarter | Metric | Value."""
    soup = BeautifulSoup(html, "lxml")
    section = soup.select_one("section#quarters")
    table = section.select_one("table") if section else None
    if table is None:
        raise ValueError(f"Quarterly results table not found for {company}")

    headers = [th.get_text(strip=True) for th in table.select("thead th")][1:]
    quarters = [datetime.strptime(h, "%b %Y") for h in headers]

    rows = []
    for tr in table.select("tbody tr"):
        cells = tr.find_all("td")
        if len(cells) < 2:
            continue
        label = _clean_label(cells[0].get_text())
        metric = config.METRIC_MAP.get(label)
        if metric is None:
            continue
        for q, cell in zip(quarters, cells[1:]):
            rows.append(
                {"Company": company, "Quarter": q, "Metric": metric,
                 "Value": _to_number(cell.get_text())}
            )
    if not rows:
        raise ValueError(f"No recognised metrics parsed for {company}")
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def scrape_company(name: str, slug: str, method: str = "auto") -> pd.DataFrame:
    url = config.SCREENER_URL.format(slug=slug)
    log.info("Scraping %s -> %s", name, url)
    html = fetch_html(url, method)
    (config.RAW_DIR / f"{slug}.html").write_text(html, encoding="utf-8")  # audit trail
    return parse_quarterly_table(html, name)


def scrape_all(companies: list[str], method: str = "auto", progress=None) -> pd.DataFrame:
    """Scrape every selected company. Failures are logged and skipped."""
    frames, failed = [], []
    for i, name in enumerate(companies, 1):
        try:
            frames.append(scrape_company(name, config.COMPANIES[name], method))
        except Exception as exc:
            log.error("Failed for %s: %s", name, exc)
            failed.append(name)
        if progress:
            progress(i / len(companies), name)
        time.sleep(1.0)  # be polite to the server
    if not frames:
        raise RuntimeError(f"Scraping failed for all companies: {failed}")
    df = pd.concat(frames, ignore_index=True)
    df.attrs["failed"] = failed
    return df
