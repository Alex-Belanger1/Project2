"""Prepare verifiable market and vintage inputs without running the strategy."""

import csv
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

from signal_test import parse_vintage

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TICKERS = ["BIL", "IEF", "LQD", "VT"]
PRICE_START = date(2021, 9, 1)
PRICE_END = date(2026, 10, 1)
VINTAGE_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}
PRICE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"


def timestamp(day):
    return int(datetime.combine(day, datetime.min.time(), timezone.utc).timestamp())


def fetch_prices(ticker):
    response = requests.get(f"{PRICE_URL}/{ticker}", params={"period1": timestamp(PRICE_START),
                            "period2": timestamp(PRICE_END), "interval": "1d"}, headers=HEADERS, timeout=25)
    response.raise_for_status()
    result, = response.json()["chart"]["result"]
    if result["meta"]["symbol"] != ticker or result["meta"]["currency"] != "USD":
        raise ValueError(f"Unexpected security or currency for {ticker}.")
    month_ends = {}
    for epoch, value in zip(result["timestamp"], result["indicators"]["adjclose"][0]["adjclose"], strict=True):
        day = datetime.fromtimestamp(epoch, timezone.utc).date()
        if PRICE_START <= day < PRICE_END and value is not None:
            month_ends[day.isoformat()[:7]] = day, value
    return ticker, month_ends, response.url, hashlib.sha256(response.content).hexdigest()


def download_vintage(cutoff):
    file = DATA / "alfred" / f"{cutoff}.csv"
    for attempt in range(3):
        try:
            if not file.exists():
                response = requests.get(VINTAGE_URL, params={"id": "FEDFUNDS", "vintage_date": str(cutoff)}, timeout=12)
                response.raise_for_status()
                source_text = response.text
            else:
                source_text = file.read_text(encoding="utf-8")
            evidence = parse_vintage(source_text, cutoff)
            if evidence is None:
                raise ValueError(f"Missing rate pair at {cutoff}.")
            # Freeze only the two monthly records used by the rule, with the original vintage header.
            compact = f"observation_date,FEDFUNDS_{evidence.effective_vintage:%Y%m%d}\n"
            compact += f"{evidence.prior_month},{evidence.prior_value}\n{evidence.latest_month},{evidence.latest_value}\n"
            file.write_text(compact, encoding="utf-8")
            return None
        except (requests.RequestException, ValueError) as exc:
            if attempt == 2:
                return f"{cutoff}: {exc}"


def main():
    (DATA / "alfred").mkdir(parents=True, exist_ok=True)
    prices_file = DATA / "verified_prices.csv"
    sessions_file = DATA / "sessions.csv"
    vendor_file = DATA / "price_sources.json"
    if not (prices_file.exists() and sessions_file.exists() and vendor_file.exists()):
        with ThreadPoolExecutor(4) as pool:
            downloads = list(pool.map(fetch_prices, TICKERS))
        months = sorted(downloads[0][1])
        if len(months) != 61 or months[0] != "2021-09" or months[-1] != "2026-09":
            raise ValueError("Price data does not cover all 61 months.")
        with prices_file.open("w", newline="", encoding="utf-8") as prices, sessions_file.open("w", newline="", encoding="utf-8") as sessions:
            p = csv.writer(prices)
            s = csv.writer(sessions)
            p.writerow(["Date", *TICKERS])
            s.writerow(["month", "last_session"])
            for month in months:
                values = [ticker_rows[month] for _, ticker_rows, _, _ in downloads]
                if len({day for day, _ in values}) != 1:
                    raise ValueError(f"Last session disagrees across ETFs in {month}.")
                p.writerow([month + "-01", *(f"{value:.8f}" for _, value in values)])
                s.writerow([month, values[0][0]])
        vendor_file.write_text(json.dumps({
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
            "sources": [{"symbol": ticker, "url": url, "raw_sha256": sha}
                        for ticker, _, url, sha in downloads],
        }, indent=2) + "\n", encoding="utf-8")
    with sessions_file.open(newline="", encoding="utf-8") as sessions:
        cutoffs = [date.fromisoformat(row["last_session"]) - timedelta(days=1)
                   for row in csv.DictReader(sessions) if row["month"] < "2026-09"]
    with ThreadPoolExecutor(12) as pool:
        errors = [res for res in pool.map(download_vintage, cutoffs) if res is not None]
    for error in errors:
        print(error)
    print(f"Verified {len(cutoffs)-len(errors)}/{len(cutoffs)} primary ALFRED cutoffs.")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
