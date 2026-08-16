"""
fetch_prices.py — pull live price, analyst target, and consensus rating
for each ticker on the watchlist, via yfinance (no API key required).

yfinance scrapes Yahoo Finance's public endpoints, so fields can be
missing or occasionally rate-limited — every lookup is wrapped so one
bad ticker never kills the whole run.
"""

from __future__ import annotations

import yfinance as yf

# (ticker, display name, country, sector)
WATCHLIST = [
    ("SNDK", "SanDisk", "United States", "chips"),
    ("MU", "Micron", "United States", "chips"),
    ("NVDA", "Nvidia", "United States", "chips"),
    ("AVGO", "Broadcom", "United States", "chips"),
    ("TSM", "Taiwan Semiconductor", "Taiwan", "chips"),
    ("AMD", "Advanced Micro Devices", "United States", "chips"),
    ("RHM.DE", "Rheinmetall", "Germany", "defense"),
    ("SAAB-B.ST", "Saab", "Sweden", "defense"),
    ("HO.PA", "Thales", "France", "defense"),
    ("LDO.MI", "Leonardo", "Italy", "defense"),
    ("BA.L", "BAE Systems", "United Kingdom", "defense"),
    ("KOG.OL", "Kongsberg Gruppen", "Norway", "defense"),
]

# Yahoo's recommendationKey -> our badge vocabulary
RATING_MAP = {
    "strong_buy": ("buy", "Strong Buy"),
    "buy": ("buy", "Buy"),
    "hold": ("hold", "Hold"),
    "sell": ("sell", "Sell"),
    "strong_sell": ("sell", "Strong Sell"),
    "none": ("hold", "N/A"),
}


def fetch_one(ticker: str, name: str, country: str, sector: str) -> dict:
    entry = {
        "ticker": ticker,
        "name": name,
        "country": country,
        "sector": sector,
        "price": None,
        "currency": None,
        "target": None,
        "rating": "hold",
        "badge": "N/A",
        "analysts": "—",
    }
    try:
        info = yf.Ticker(ticker).get_info()
        entry["price"] = info.get("currentPrice") or info.get("regularMarketPrice")
        entry["currency"] = info.get("currency")

        target = info.get("targetMeanPrice")
        if target:
            entry["target"] = f"{target:,.0f} {entry['currency'] or ''}".strip()

        n_analysts = info.get("numberOfAnalystOpinions")
        if n_analysts:
            entry["analysts"] = f"{n_analysts} analysts"

        key = (info.get("recommendationKey") or "none").lower()
        rating, badge = RATING_MAP.get(key, ("hold", "N/A"))
        entry["rating"] = rating
        entry["badge"] = badge
    except Exception as exc:  # noqa: BLE001 — one bad ticker shouldn't kill the run
        entry["error"] = str(exc)
    return entry


def fetch_all() -> list[dict]:
    return [fetch_one(*row) for row in WATCHLIST]


if __name__ == "__main__":
    import json
    print(json.dumps(fetch_all(), indent=2))
