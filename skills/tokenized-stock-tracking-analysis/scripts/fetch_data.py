#!/usr/bin/env python3
"""
Fetch US stock data (yfinance) and tokenized stock data (CoinGecko).

Usage:
    python fetch_data.py --stock-ticker MU --coin-id micron-technology-ondo-tokenized-stock --output-dir ./output
    python fetch_data.py --stock-ticker NVDA --coin-id nvidia-ondo-tokenized-stock --output-dir ./output
"""

import argparse
import sys
import time
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
import pandas as pd
import urllib3
urllib3.disable_warnings()

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}


def fetch_stock_yahoo(ticker: str, output_dir: Path):
    """Download US stock daily data via Yahoo Finance chart API."""
    print(f"\n{'='*50}")
    print(f"Downloading stock data: {ticker}")
    print(f"{'='*50}")

    period1 = int(datetime(2010, 1, 1).timestamp())
    period2 = int(datetime.now(timezone.utc).timestamp())

    url = (f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?period1={period1}&period2={period2}&interval=1d&events=div,splits")

    for attempt in range(5):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                break
            elif r.status_code == 429:
                wait = (attempt + 1) * 10
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  HTTP {r.status_code}: {r.text[:150]}")
                time.sleep(3)
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    else:
        raise RuntimeError(f"Failed to fetch {ticker} after 5 attempts")

    data = r.json()
    result = data.get('chart', {}).get('result', [])
    if not result:
        raise RuntimeError(f"No data in Yahoo response for {ticker}")

    meta = result[0]['meta']
    print(f"  Symbol: {meta.get('symbol')}, Currency: {meta.get('currency')}")
    print(f"  Exchange: {meta.get('exchangeName')}")

    ts = result[0]['timestamp']
    quotes = result[0]['indicators']['quote'][0]

    df = pd.DataFrame({
        'Date': pd.to_datetime(ts, unit='s'),
        'Open': quotes['open'],
        'High': quotes['high'],
        'Low': quotes['low'],
        'Close': quotes['close'],
        'Volume': quotes['volume'],
    })

    adj = result[0]['indicators'].get('adjclose', [])
    if adj and 'adjclose' in adj[0]:
        df['Adj Close'] = adj[0]['adjclose']
    else:
        df['Adj Close'] = df['Close']

    df = df.dropna(subset=['Close']).sort_values('Date').reset_index(drop=True)

    out = output_dir / 'raw_stock.csv'
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"  Saved: {out}")
    print(f"  Rows: {len(df)}, Range: {df['Date'].iloc[0]} ~ {df['Date'].iloc[-1]}")
    return df


def fetch_tokenized_coingecko(coin_id: str, output_dir: Path):
    """Download tokenized stock hourly data via CoinGecko range API."""
    print(f"\n{'='*50}")
    print(f"Downloading tokenized data: {coin_id}")
    print(f"{'='*50}")

    # First check how far back data goes with days=365
    url_check = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=365"
    r = requests.get(url_check, timeout=30)
    if r.status_code != 200:
        # Try getting coin info for genesis date
        url_info = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        r2 = requests.get(url_info, timeout=30)
        if r2.status_code == 200:
            info = r2.json()
            genesis = info.get('genesis_date')
            print(f"  Genesis date: {genesis}")
        # Default to ~9 months ago
        start = datetime.now(timezone.utc) - timedelta(days=365)
    else:
        prices_check = r.json().get('prices', [])
        if prices_check:
            start = datetime.fromtimestamp(prices_check[0][0]/1000, tz=timezone.utc)
        else:
            start = datetime.now(timezone.utc) - timedelta(days=365)

    print(f"  Fetching from: {start.date()}")

    # Download in 30-day chunks for ~1h granularity
    all_prices = []
    cursor = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = datetime.now(timezone.utc) + timedelta(days=1)
    chunk_num = 0

    while cursor < end:
        chunk_end = min(cursor + timedelta(days=30), end)
        from_ts = int(cursor.timestamp())
        to_ts = int(chunk_end.timestamp())

        url = (f"https://api.coingecko.com/api/v3/coins/{coin_id}/"
               f"market_chart/range?vs_currency=usd&from={from_ts}&to={to_ts}")

        try:
            r = requests.get(url, timeout=30)
            chunk_num += 1

            if r.status_code == 200:
                p = r.json().get('prices', [])
                all_prices.extend(p)
                gap = ""
                if len(p) >= 2:
                    gap_h = (p[1][0] - p[0][0]) / 3600000
                    gap = f"gap ~{gap_h:.1f}h"
                print(f"  Chunk {chunk_num}: {cursor.date()}~{chunk_end.date()} → {len(p)} pts {gap} (total: {len(all_prices)})")
            elif r.status_code == 429:
                print(f"  Chunk {chunk_num}: rate limited, waiting 30s...")
                time.sleep(30)
                continue
            else:
                print(f"  Chunk {chunk_num}: HTTP {r.status_code} {r.text[:80]}")
                time.sleep(2)
        except Exception as e:
            print(f"  Chunk {chunk_num}: error {e}, retrying...")
            time.sleep(5)
            continue

        cursor = chunk_end
        time.sleep(1.5)

    # Deduplicate
    seen = set()
    unique = []
    for p in all_prices:
        if p[0] not in seen:
            seen.add(p[0])
            unique.append(p)
    unique.sort(key=lambda x: x[0])

    if not unique:
        raise RuntimeError(f"No price data retrieved for {coin_id}")

    # Convert to DataFrame
    df = pd.DataFrame(unique, columns=['ts_ms', 'tokenized_price'])
    df['datetime_utc'] = pd.to_datetime(df['ts_ms'], unit='ms', utc=True)
    df = df[['ts_ms', 'datetime_utc', 'tokenized_price']]

    out = output_dir / 'raw_tokenized_price.csv'
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    t0 = df['datetime_utc'].iloc[0]
    t1 = df['datetime_utc'].iloc[-1]
    if len(df) >= 2:
        gaps = [(df['ts_ms'].iloc[i] - df['ts_ms'].iloc[i-1])/3600000 for i in range(1, min(20, len(df)))]
        avg_gap = sum(gaps) / len(gaps)
    else:
        avg_gap = 0

    print(f"  Saved: {out}")
    print(f"  Rows: {len(df)}, Range: {t0} ~ {t1}, Avg gap: {avg_gap:.1f}h")
    return df


def main():
    parser = argparse.ArgumentParser(description='Fetch stock and tokenized stock data')
    parser.add_argument('--stock-ticker', required=True, help='Yahoo Finance ticker, e.g. MU, NVDA')
    parser.add_argument('--coin-id', required=True, help='CoinGecko coin ID')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    try:
        fetch_stock_yahoo(args.stock_ticker, output_dir)
    except Exception as e:
        print(f"ERROR fetching stock data: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        fetch_tokenized_coingecko(args.coin_id, output_dir)
    except Exception as e:
        print(f"ERROR fetching tokenized data: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n✓ Data fetch complete. Files in: {output_dir}")


if __name__ == '__main__':
    main()
