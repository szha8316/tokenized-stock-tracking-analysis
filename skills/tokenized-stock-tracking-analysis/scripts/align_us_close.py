#!/usr/bin/env python3
"""
Align tokenized stock prices to US market close (NY 16:00).

Usage:
    python align_us_close.py --input-dir ./output --max-time-diff-minutes 90
"""

import argparse
import sys
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

import pandas as pd
import numpy as np


def align_to_us_close(input_dir: Path, max_time_diff_minutes: int = 90):
    """Align tokenized hourly prices to each stock trading day's NY 16:00."""
    ny_tz = ZoneInfo('America/New_York')

    # Read
    stock_path = input_dir / 'raw_stock.csv'
    token_path = input_dir / 'raw_tokenized_price.csv'

    if not stock_path.exists():
        raise FileNotFoundError(f"Stock data not found: {stock_path}")
    if not token_path.exists():
        raise FileNotFoundError(f"Tokenized data not found: {token_path}")

    mu = pd.read_csv(stock_path)
    mu['Date'] = pd.to_datetime(mu['Date'])
    # Extract NY date from timestamp
    mu['ny_date'] = mu['Date'].dt.tz_localize(timezone.utc).dt.tz_convert(ny_tz).dt.date
    mu = mu.sort_values('ny_date').reset_index(drop=True)

    token = pd.read_csv(token_path)
    token['datetime_utc'] = pd.to_datetime(token['datetime_utc'], format='mixed')
    token = token.sort_values('datetime_utc').reset_index(drop=True)

    print(f"Stock: {mu['ny_date'].iloc[0]} ~ {mu['ny_date'].iloc[-1]}, {len(mu)} rows")
    print(f"Token: {token['datetime_utc'].iloc[0]} ~ {token['datetime_utc'].iloc[-1]}, {len(token)} rows")

    # Align
    results = []
    for _, row in mu.iterrows():
        d = row['ny_date']
        adj_c = row['Adj Close']
        close = row['Close']

        ny_close = datetime(d.year, d.month, d.day, 16, 0, 0, tzinfo=ny_tz)
        ny_close_utc = ny_close.astimezone(timezone.utc)

        window_s = ny_close_utc - timedelta(hours=4)
        window_e = ny_close_utc + timedelta(hours=4)
        candidates = token[(token['datetime_utc'] >= window_s) & (token['datetime_utc'] <= window_e)].copy()

        if len(candidates) > 0:
            candidates['time_diff'] = abs((candidates['datetime_utc'] - ny_close_utc).dt.total_seconds())
            best = candidates.loc[candidates['time_diff'].idxmin()]
            snap_price = best['tokenized_price']
            matched_time = best['datetime_utc']
            td_min = best['time_diff'] / 60
            low_q = 1 if td_min > max_time_diff_minutes else 0
        else:
            snap_price = np.nan
            matched_time = pd.NaT
            td_min = np.nan
            low_q = 1

        results.append({
            'date': d,
            'us_close_time_utc': ny_close_utc,
            'tokenized_matched_time_utc': matched_time,
            'time_diff_minutes': td_min,
            'stock_close': close,
            'stock_adj_close': adj_c,
            'tokenized_price_at_us_close': snap_price,
            'low_quality_match': low_q,
        })

    aligned = pd.DataFrame(results)

    # Filter: only dates with tokenized data
    aligned = aligned.dropna(subset=['tokenized_price_at_us_close']).reset_index(drop=True)

    # Calculate returns
    aligned_lq = aligned[aligned['low_quality_match'] == 0].copy()
    aligned_lq['stock_return'] = aligned_lq['stock_adj_close'].pct_change()
    aligned_lq['tokenized_return'] = aligned_lq['tokenized_price_at_us_close'].pct_change()
    aligned_lq['premium_discount'] = aligned_lq['tokenized_price_at_us_close'] / aligned_lq['stock_adj_close'] - 1

    aligned_lq = aligned_lq.sort_values('date').reset_index(drop=True)

    # Stats
    print(f"\nAlignment results:")
    print(f"  Total matched: {len(aligned)}")
    print(f"  Low quality (>{max_time_diff_minutes}min): {aligned['low_quality_match'].sum()}")
    print(f"  time_diff: mean={aligned['time_diff_minutes'].mean():.1f}min, "
          f"median={aligned['time_diff_minutes'].median():.1f}min, "
          f"max={aligned['time_diff_minutes'].max():.1f}min")
    print(f"  Valid after quality filter: {len(aligned_lq)}")
    print(f"  Range: {aligned_lq['date'].iloc[0]} ~ {aligned_lq['date'].iloc[-1]}")

    # Save
    out = input_dir / 'us_close_aligned.csv'
    aligned_lq.to_csv(out, index=False, float_format='%.10f')
    print(f"  Saved: {out}")


def main():
    parser = argparse.ArgumentParser(description='Align tokenized prices to NY 16:00')
    parser.add_argument('--input-dir', required=True, help='Directory with raw_stock.csv and raw_tokenized_price.csv')
    parser.add_argument('--max-time-diff-minutes', type=int, default=90, help='Max allowed time diff (default: 90)')
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    align_to_us_close(input_dir, args.max_time_diff_minutes)


if __name__ == '__main__':
    main()
