#!/usr/bin/env python3
"""
Analyze tracking quality: correlation, regression, tracking error, premium/discount, NAV.

Usage:
    python analyze_tracking.py --input-dir ./output
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def analyze(input_dir: Path):
    """Run full tracking analysis."""
    aligned_path = input_dir / 'us_close_aligned.csv'
    if not aligned_path.exists():
        raise FileNotFoundError(f"Aligned data not found: {aligned_path}")

    df = pd.read_csv(aligned_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.dropna(subset=['stock_return', 'tokenized_return']).sort_values('date').reset_index(drop=True)

    print(f"Analyzing: {len(df)} rows, {df['date'].iloc[0].date()} ~ {df['date'].iloc[-1].date()}")

    # --- Correlation ---
    price_corr = df['stock_adj_close'].corr(df['tokenized_price_at_us_close'])
    pearson = df['stock_return'].corr(df['tokenized_return'])
    spearman = df['stock_return'].corr(df['tokenized_return'], method='spearman')

    # --- Regression ---
    X = df[['stock_return']].values
    y = df['tokenized_return'].values
    reg = LinearRegression().fit(X, y)
    alpha = float(reg.intercept_)
    beta = float(reg.coef_[0])
    r_sq = float(reg.score(X, y))

    # --- Tracking error ---
    df['return_diff'] = df['tokenized_return'] - df['stock_return']
    rd = df['return_diff']
    rd_mean = rd.mean()
    rd_median = rd.median()
    rd_std = rd.std()
    rd_mae = rd.abs().mean()
    rd_max_pos = rd.max()
    rd_max_neg = rd.min()
    rd_max_abs = rd.abs().max()
    ann_te = rd_std * np.sqrt(252)

    # --- Premium/Discount ---
    df['premium_discount'] = df['tokenized_price_at_us_close'] / df['stock_adj_close'] - 1
    pd_series = df['premium_discount']
    pd_mean = pd_series.mean()
    pd_median = pd_series.median()
    pd_std = pd_series.std()
    pd_mae = pd_series.abs().mean()
    pd_max = pd_series.max()
    pd_min = pd_series.min()
    pd_max_abs = pd_series.abs().max()

    within_1 = (pd_series.abs() <= 0.01).mean()
    within_2 = (pd_series.abs() <= 0.02).mean()

    # --- NAV ---
    df['stock_nav'] = (1 + df['stock_return']).cumprod()
    df['tokenized_nav'] = (1 + df['tokenized_return']).cumprod()

    final_stock = df['stock_nav'].iloc[-1]
    final_token = df['tokenized_nav'].iloc[-1]
    stock_cum = final_stock - 1
    token_cum = final_token - 1
    long_gap = final_token / final_stock - 1

    # --- Top deviation dates ---
    df_rd = df.nlargest(10, df['return_diff'].abs())
    cols_rd = ['date', 'stock_adj_close', 'tokenized_price_at_us_close',
               'stock_return', 'tokenized_return', 'return_diff',
               'premium_discount', 'time_diff_minutes']
    df_rd[cols_rd].to_csv(input_dir / 'top_return_diff_dates.csv', index=False, float_format='%.8f')

    df_pd = df.nlargest(10, df['premium_discount'].abs())
    cols_pd = ['date', 'stock_adj_close', 'tokenized_price_at_us_close',
               'premium_discount', 'stock_return', 'tokenized_return',
               'return_diff', 'time_diff_minutes']
    df_pd[cols_pd].to_csv(input_dir / 'top_premium_discount_dates.csv', index=False, float_format='%.8f')

    # --- Summary ---
    summary = pd.DataFrame([{
        'sample_start_date': str(df['date'].iloc[0].date()),
        'sample_end_date': str(df['date'].iloc[-1].date()),
        'sample_size': len(df),
        'price_corr': round(price_corr, 6),
        'pearson_return_corr': round(pearson, 6),
        'spearman_return_corr': round(spearman, 6),
        'regression_alpha': round(alpha, 8),
        'regression_beta': round(beta, 6),
        'regression_r_squared': round(r_sq, 6),
        'return_diff_mean': round(rd_mean, 8),
        'return_diff_median': round(rd_median, 8),
        'return_diff_std': round(rd_std, 8),
        'return_diff_mean_abs': round(rd_mae, 8),
        'return_diff_max_positive': round(rd_max_pos, 8),
        'return_diff_max_negative': round(rd_max_neg, 8),
        'return_diff_max_abs': round(rd_max_abs, 8),
        'annualized_tracking_error': round(ann_te, 8),
        'premium_discount_mean': round(pd_mean, 8),
        'premium_discount_median': round(pd_median, 8),
        'premium_discount_std': round(pd_std, 8),
        'premium_discount_mean_abs': round(pd_mae, 8),
        'premium_discount_max': round(pd_max, 8),
        'premium_discount_min': round(pd_min, 8),
        'premium_discount_max_abs': round(pd_max_abs, 8),
        'percent_within_1pct': round(within_1, 6),
        'percent_within_2pct': round(within_2, 6),
        'final_stock_nav': round(final_stock, 6),
        'final_tokenized_nav': round(final_token, 6),
        'stock_cumulative_return': round(stock_cum, 8),
        'tokenized_cumulative_return': round(token_cum, 8),
        'long_term_gap': round(long_gap, 8),
        'avg_time_diff_minutes': round(df['time_diff_minutes'].mean(), 2),
        'max_time_diff_minutes': round(df['time_diff_minutes'].max(), 2),
    }])
    summary.to_csv(input_dir / 'tracking_summary.csv', index=False)

    # --- Full analysis table ---
    df.to_csv(input_dir / 'tracking_analysis.csv', index=False, float_format='%.10f')

    print(f"  Saved: tracking_summary.csv")
    print(f"  Saved: tracking_analysis.csv")
    print(f"  Saved: top_return_diff_dates.csv")
    print(f"  Saved: top_premium_discount_dates.csv")

    # Print key metrics
    print(f"\n{'='*50}")
    print(f"  Key Metrics")
    print(f"{'='*50}")
    print(f"  Pearson r:        {pearson:.4f}")
    print(f"  Spearman:         {spearman:.4f}")
    print(f"  Beta:             {beta:.4f}")
    print(f"  Alpha:            {alpha*100:+.4f}%")
    print(f"  R²:               {r_sq:.4f}")
    print(f"  Annualized TE:    {ann_te*100:.2f}%")
    print(f"  Mean P/D:         {pd_mean*100:+.4f}%")
    print(f"  Max Premium:      {pd_max*100:+.4f}%")
    print(f"  Max Discount:     {pd_min*100:+.4f}%")
    print(f"  ±2% within:       {within_2*100:.0f}%")
    print(f"  Stock cum:        {stock_cum*100:+.2f}%")
    print(f"  Token cum:        {token_cum*100:+.2f}%")
    print(f"  Long-term gap:    {long_gap*100:+.2f}%")

    return df, summary


def main():
    parser = argparse.ArgumentParser(description='Analyze tokenized stock tracking quality')
    parser.add_argument('--input-dir', required=True, help='Directory with us_close_aligned.csv')
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    analyze(input_dir)
    print(f"\n✓ Analysis complete.")


if __name__ == '__main__':
    main()
