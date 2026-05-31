#!/usr/bin/env python3
"""
Generate 5 standard tracking analysis charts.

Usage:
    python plot_charts.py --input-dir ./output
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression

# Default sans-serif fonts
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False


def plot_all(input_dir: Path, stock_ticker: str = 'Stock', tokenized_symbol: str = 'Token'):
    """Generate all 5 charts."""
    analysis_path = input_dir / 'tracking_analysis.csv'
    if not analysis_path.exists():
        raise FileNotFoundError(f"Analysis data not found: {analysis_path}")

    df = pd.read_csv(analysis_path)
    df['date'] = pd.to_datetime(df['date'])

    charts_dir = input_dir / 'charts'
    charts_dir.mkdir(parents=True, exist_ok=True)

    # Ensure return_diff
    if 'return_diff' not in df.columns:
        df['return_diff'] = df['tokenized_return'] - df['stock_return']

    # Pre-compute stats
    te_pct = df['return_diff'] * 100
    pd_pct = df['premium_discount'] * 100

    X = df[['stock_return']].values
    y = df['tokenized_return'].values
    reg = LinearRegression().fit(X, y)
    beta = float(reg.coef_[0])
    alpha = float(reg.intercept_)
    r_sq = float(reg.score(X, y))
    pearson = df['stock_return'].corr(df['tokenized_return'])

    # ═══ Chart 1: NAV Comparison ═══
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(df['date'], df['stock_nav'], label=f'{stock_ticker} (Spot)', lw=2, color='#2E86AB')
    ax.plot(df['date'], df['tokenized_nav'], label=f'{tokenized_symbol} (Tokenized)', lw=2, color='#D1495B')
    ax.set_title(f'{stock_ticker} vs {tokenized_symbol} NAV Comparison', fontsize=14, fontweight='bold')
    ax.set_ylabel('NAV (Base = 1)')
    ax.legend(loc='upper left', fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.tick_params(axis='x', rotation=35, labelsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(charts_dir / '01_nav_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()

    # ═══ Chart 2: Return Scatter ═══
    fig, ax = plt.subplots(figsize=(8, 8))
    sr = df['stock_return'] * 100
    tr = df['tokenized_return'] * 100
    ax.scatter(sr, tr, alpha=0.5, s=25, color='#2E86AB', edgecolors='white', linewidth=0.3)
    l = max(abs(sr).max(), abs(tr).max()) * 1.1
    xl = np.array([-l, l])
    ax.plot(xl, xl, '--', color='grey', lw=1, label='y = x (Perfect 1:1)')
    ax.plot(xl, reg.predict(xl.reshape(-1, 1)/100)*100, '-', color='#D1495B', lw=1.8,
            label=f'Regression: y = {beta:.3f}x + {alpha*100:+.3f}%')
    ax.set_xlim(-l, l); ax.set_ylim(-l, l)
    ax.set_xlabel(f'{stock_ticker} Daily Return (%)', fontsize=11)
    ax.set_ylabel(f'{tokenized_symbol} Daily Return (%)', fontsize=11)
    ax.set_title(f'{tokenized_symbol} Daily Return vs {stock_ticker} Daily Return', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    info = f'Pearson r = {pearson:.4f}\nbeta = {beta:.4f}\nR² = {r_sq:.4f}\nn = {len(df)}'
    ax.text(0.03, 0.97, info, transform=ax.transAxes, fontsize=10, va='top', ha='left',
            family='monospace', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    plt.tight_layout()
    plt.savefig(charts_dir / '02_return_scatter.png', dpi=150, bbox_inches='tight')
    plt.close()

    # ═══ Chart 3: Return Diff Timeseries ═══
    fig, ax = plt.subplots(figsize=(13, 5))
    colors = ['#D1495B' if v >= 0 else '#2E86AB' for v in te_pct]
    ax.bar(df['date'], te_pct, color=colors, alpha=0.75, width=1)
    ax.axhline(y=0, color='black', lw=0.8)
    ax.set_xlabel('Date')
    ax.set_ylabel('Return Difference (%)')
    ann_te = te_pct.std() * np.sqrt(252)
    ax.set_title(f'Daily Return Difference ({tokenized_symbol} - {stock_ticker})', fontsize=14, fontweight='bold')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.tick_params(axis='x', rotation=35, labelsize=9)
    ax.grid(True, alpha=0.3)
    ax.text(0.985, 0.95, f'Mean: {te_pct.mean():+.3f}%\nStd: {te_pct.std():.3f}%\nAnn TE: {ann_te:.1f}%',
            transform=ax.transAxes, fontsize=9, va='top', ha='right', family='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    plt.tight_layout()
    plt.savefig(charts_dir / '03_return_diff_timeseries.png', dpi=150, bbox_inches='tight')
    plt.close()

    # ═══ Chart 4: Premium/Discount Timeseries ═══
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.fill_between(df['date'], pd_pct, 0, where=pd_pct >= 0,
                    color='#D1495B', alpha=0.5, label='Premium (Token > Spot)')
    ax.fill_between(df['date'], pd_pct, 0, where=pd_pct < 0,
                    color='#2E86AB', alpha=0.5, label='Discount (Token < Spot)')
    ax.axhline(y=0, color='black', lw=0.8)
    ax.set_xlabel('Date')
    ax.set_ylabel('Premium / Discount (%)')
    ax.set_title(f'{tokenized_symbol} Premium / Discount vs {stock_ticker} (NY 16:00 Snap)', fontsize=14, fontweight='bold')
    ax.legend(loc='lower left', fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.tick_params(axis='x', rotation=35, labelsize=9)
    ax.grid(True, alpha=0.3)
    within_2 = (pd_pct.abs() <= 2).mean() * 100
    ax.text(0.985, 0.95, f'Mean: {pd_pct.mean():+.3f}%\n±2% within: {within_2:.0f}%',
            transform=ax.transAxes, fontsize=9, va='top', ha='right', family='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    plt.tight_layout()
    plt.savefig(charts_dir / '04_premium_discount_timeseries.png', dpi=150, bbox_inches='tight')
    plt.close()

    # ═══ Chart 5: Premium/Discount Histogram ═══
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(pd_pct, bins=28, color='#2E86AB', alpha=0.7, edgecolor='white', linewidth=0.5)
    ax.axvline(x=0, color='black', lw=1, label='0% (Parity)')
    ax.axvline(x=pd_pct.mean(), color='#D1495B', lw=1.2, ls='--', label=f'Mean: {pd_pct.mean():+.3f}%')
    ax.set_xlabel('Premium / Discount (%)', fontsize=11)
    ax.set_ylabel('Frequency (Days)', fontsize=11)
    ax.set_title('Premium / Discount Distribution', fontsize=14, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    ax.text(0.97, 0.95, f'±2% within: {within_2:.0f}%\nStd: {pd_pct.std():.3f}%',
            transform=ax.transAxes, fontsize=9, va='top', ha='right', family='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    plt.tight_layout()
    plt.savefig(charts_dir / '05_premium_discount_histogram.png', dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  5 charts saved to {charts_dir}/")


def main():
    parser = argparse.ArgumentParser(description='Plot tracking analysis charts')
    parser.add_argument('--input-dir', required=True, help='Directory with tracking_analysis.csv')
    parser.add_argument('--stock-ticker', default='Stock', help='Stock ticker for chart labels')
    parser.add_argument('--tokenized-symbol', default='Token', help='Tokenized symbol for chart labels')
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    plot_all(input_dir, args.stock_ticker, args.tokenized_symbol)
    print(f"\n✓ Charts generated.")


if __name__ == '__main__':
    main()
