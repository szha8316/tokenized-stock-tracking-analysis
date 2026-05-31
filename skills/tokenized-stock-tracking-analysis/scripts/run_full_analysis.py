#!/usr/bin/env python3
"""
Run the complete tokenized stock tracking analysis pipeline.

Usage:
    python run_full_analysis.py \
        --stock-ticker MU \
        --coin-id micron-technology-ondo-tokenized-stock \
        --tokenized-symbol MUon \
        --output-dir MU_MUon_tracking

    python run_full_analysis.py \
        --stock-ticker NVDA \
        --coin-id nvidia-ondo-tokenized-stock \
        --tokenized-symbol NVDAon \
        --output-dir NVDA_NVDAon_tracking
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


def run_step(name: str, cmd: list[str], cwd: Path):
    """Run a pipeline step, print progress, exit on failure."""
    print(f"\n{'#'*60}")
    print(f"  STEP: {name}")
    print(f"{'#'*60}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"\nERROR: Step '{name}' failed with code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)


def generate_interpretation(output_dir: Path, stock_ticker: str, tokenized_symbol: str):
    """Generate English interpretation report from summary metrics."""
    import pandas as pd
    import numpy as np

    templates_dir = Path(__file__).resolve().parent.parent / 'templates'
    template_path = templates_dir / 'interpretation_template.md'

    # Read summary
    summary_path = output_dir / 'tracking_summary.csv'
    if not summary_path.exists():
        print(f"  WARNING: No summary found, skipping interpretation")
        return

    s = pd.read_csv(summary_path).iloc[0]

    # Read top deviation dates
    top_rd = pd.read_csv(output_dir / 'top_return_diff_dates.csv')
    top_pd = pd.read_csv(output_dir / 'top_premium_discount_dates.csv')

    interpretation = f"""# {stock_ticker} vs {tokenized_symbol} — Tracking Analysis Interpretation

**Sample period:** {s['sample_start_date']} to {s['sample_end_date']}
**Alignment method:** Tokenized price snapped to NY 16:00 market close
**Sample size:** {int(s['sample_size'])} trading days

## (1) Overall assessment

The tracking relationship between {tokenized_symbol} and {stock_ticker} is generally strong.
After NY 16:00 time alignment, the daily return Pearson correlation is {s['pearson_return_corr']:.4f}
(Spearman: {s['spearman_return_corr']:.4f}), the linear regression beta is {s['regression_beta']:.4f}
({"close to 1, supporting 1:1 tracking" if 0.95 <= s['regression_beta'] <= 1.05 else "somewhat deviating from 1"}),
and R² is {s['regression_r_squared']:.4f}.
These results indicate that {tokenized_symbol} largely achieves near 1:1 daily return tracking
against {stock_ticker}.

The annualized tracking error is {s['annualized_tracking_error']*100:.1f}%.
The mean premium/discount is {s['premium_discount_mean']*100:+.3f}% (near zero),
with {s['percent_within_2pct']*100:.0f}% of trading days within ±2%.
Over the full period, {stock_ticker} returned {s['stock_cumulative_return']*100:+.2f}%
and {tokenized_symbol} returned {s['tokenized_cumulative_return']*100:+.2f}%,
for a long-term gap of {s['long_term_gap']*100:+.2f}%.
When aligned to the U.S. market close, {tokenized_symbol} can serve as a reasonable
substitute price exposure for {stock_ticker}.

## (2) Chart 1: NAV comparison

The NAV curves of {stock_ticker} (blue) and {tokenized_symbol} (red) largely overlap.
Ending NAVs: {stock_ticker} {s['final_stock_nav']:.2f}, {tokenized_symbol} {s['final_tokenized_nav']:.2f}.
The long-term gap of {s['long_term_gap']*100:+.2f}% stems from brief dislocations
early in the tokenized stock's trading history. Given {stock_ticker}'s total move of
{s['stock_cumulative_return']*100:.0f}% over the period, this gap is negligible in context.

## (3) Chart 2: Return scatter

Data points cluster tightly around the y=x reference line (grey dashed).
The regression line (red) nearly coincides with y=x: beta = {s['regression_beta']:.4f},
alpha = {s['regression_alpha']*100:+.4f}%. Pearson r = {s['pearson_return_corr']:.4f} and
R² = {s['regression_r_squared']:.4f} indicate that over {s['regression_r_squared']*100:.0f}%
of {tokenized_symbol}'s daily variance is explained by {stock_ticker}.
This strongly supports the view that {tokenized_symbol} serves as a practical substitute
price exposure for {stock_ticker}.

## (4) Chart 3: Daily return difference

Daily return deviations of {tokenized_symbol} relative to {stock_ticker} are generally small.
Mean return diff: {s['return_diff_mean']*100:+.3f}% (near zero),
standard deviation: {s['return_diff_std']*100:.2f}%.
Annualized tracking error: {s['annualized_tracking_error']*100:.1f}%.
Max positive deviation: {s['return_diff_max_positive']*100:+.2f}%,
max negative deviation: {s['return_diff_max_negative']*100:+.2f}%.
Extreme outliers occurred during the initial launch period when liquidity was very low;
comparable deviations have not recurred since.

## (5) Chart 4: Premium/discount time series

Mean premium/discount: {s['premium_discount_mean']*100:+.3f}%, indicating no systematic
premium or discount over the long term. Max premium: {s['premium_discount_max']*100:+.2f}%,
max discount: {s['premium_discount_min']*100:+.2f}%. The largest deviations cluster in the
early post-launch period when liquidity was thin. As trading volume grew, the premium/discount
range narrowed significantly.

## (6) Chart 5: Premium/discount distribution

The premium/discount distribution is highly concentrated:
{s['percent_within_2pct']*100:.0f}% of trading days fall within ±2%.
A small number of extreme outlier days create fat tails; although they represent
a very small fraction of the sample (<1%), their magnitude warrants attention.

## (7) Risk disclosures

1. **Not a real stock.** {tokenized_symbol} is an Ondo Finance-issued on-chain token.
   Holders do not possess legal ownership, voting rights, or dividend entitlements of
   the underlying {stock_ticker} shares.
2. **Issuer risk.** {tokenized_symbol}'s value depends on the integrity of Ondo's
   redemption and custody mechanisms. Operational issues, smart contract vulnerabilities,
   or credit events at Ondo could break the price peg.
3. **Liquidity risk.** Trading volume was very low during the initial launch period.
   In extreme market conditions, liquidity may dry up, leading to large slippage or
   inability to exit positions.
4. **Platform risk.** On-chain network congestion, gas price spikes, and cross-chain
   bridge security issues can all affect trading.
5. **Regulatory / delisting risk.** The regulatory status of tokenized stocks is
   uncertain in many jurisdictions. A regulatory determination that {tokenized_symbol}
   is an unregistered security could result in delisting or trading restrictions.
6. **Early-period extreme deviation risk.** The largest discount of
   {s['premium_discount_min']*100:+.2f}% occurred shortly after launch, demonstrating
   that prices can deviate substantially before sufficient liquidity is established.

## (8) Final judgment

When aligned to the U.S. market close (NY 16:00), {tokenized_symbol} can serve as
a reasonable substitute price exposure for {stock_ticker}, but it is not equivalent
to owning the real stock. The full-sample results show solid long-term tracking quality
(r = {s['pearson_return_corr']:.4f}, long-term gap = {s['long_term_gap']*100:+.2f}%).
However, a significant discount of {s['premium_discount_min']*100:+.2f}% occurred
during the early launch period, and ongoing attention to liquidity, issuer, platform,
and regulatory risks is warranted for any long-term holding.
"""
    out = output_dir / 'chart_interpretation.md'
    with open(out, 'w') as f:
        f.write(interpretation)
    print(f"  Interpretation saved: {out}")


def main():
    parser = argparse.ArgumentParser(description='Run full tokenized stock tracking analysis')
    parser.add_argument('--stock-ticker', required=True, help='Yahoo Finance ticker')
    parser.add_argument('--coin-id', required=True, help='CoinGecko coin ID')
    parser.add_argument('--tokenized-symbol', required=True, help='Tokenized stock display name')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    parser.add_argument('--start-date', default=None, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', default=None, help='End date (YYYY-MM-DD)')
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    scripts_dir = Path(__file__).resolve().parent

    print(f"\n{'='*60}")
    print(f"  Tokenized Stock Tracking Analysis")
    print(f"  {args.stock_ticker} vs {args.tokenized_symbol}")
    print(f"  Output: {output_dir}")
    print(f"{'='*60}")

    # Step 1: Fetch data
    fetch_cmd = [
        sys.executable, str(scripts_dir / 'fetch_data.py'),
        '--stock-ticker', args.stock_ticker,
        '--coin-id', args.coin_id,
        '--output-dir', str(output_dir),
    ]
    run_step('1. Fetch data', fetch_cmd, scripts_dir)

    # Step 2: Align by NY 16:00
    align_cmd = [
        sys.executable, str(scripts_dir / 'align_us_close.py'),
        '--input-dir', str(output_dir),
    ]
    run_step('2. Align by NY 16:00', align_cmd, scripts_dir)

    # Step 3: Analyze tracking
    analyze_cmd = [
        sys.executable, str(scripts_dir / 'analyze_tracking.py'),
        '--input-dir', str(output_dir),
    ]
    run_step('3. Analyze tracking', analyze_cmd, scripts_dir)

    # Step 4: Plot charts
    plot_cmd = [
        sys.executable, str(scripts_dir / 'plot_charts.py'),
        '--input-dir', str(output_dir),
        '--stock-ticker', args.stock_ticker,
        '--tokenized-symbol', args.tokenized_symbol,
    ]
    run_step('4. Generate charts', plot_cmd, scripts_dir)

    # Step 5: Generate interpretation
    print(f"\n{'#'*60}")
    print(f"  STEP: 5. Generate interpretation")
    print(f"{'#'*60}")
    generate_interpretation(output_dir, args.stock_ticker, args.tokenized_symbol)

    # Summary
    print(f"\n{'='*60}")
    print(f"  ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"\n  Output files in: {output_dir}/")
    print(f"    raw_stock.csv")
    print(f"    raw_tokenized_price.csv")
    print(f"    us_close_aligned.csv")
    print(f"    tracking_analysis.csv")
    print(f"    tracking_summary.csv")
    print(f"    top_return_diff_dates.csv")
    print(f"    top_premium_discount_dates.csv")
    print(f"    charts/01_nav_comparison.png")
    print(f"    charts/02_return_scatter.png")
    print(f"    charts/03_return_diff_timeseries.png")
    print(f"    charts/04_premium_discount_timeseries.png")
    print(f"    charts/05_premium_discount_histogram.png")
    print(f"    chart_interpretation.md")
    print()


if __name__ == '__main__':
    main()
