# Tokenized Stock Tracking Analysis Skill

A complete analysis workflow for evaluating the tracking quality between a real U.S. stock and its Ondo tokenized stock equivalent.

This skill is designed for use with Claude Code and can also be run directly as a Python-based research workflow.

> **Disclaimer:** This repository is for research, educational, and analytical practice purposes only. It is not investment advice, financial advice, trading advice, legal advice, or tax advice. Cryptocurrency, digital assets, and tokenized stock products involve significant risk, including possible loss of capital.

## Installation

### 1. Install Python dependencies

```bash
pip install pandas numpy yfinance requests matplotlib scipy scikit-learn python-dateutil pytz
```

Python 3.9 or later is required. The workflow uses timezone-aware market close alignment.

### 2. Install the skill for Claude Code

Copy the skill into your Claude Code skills directory. From the repository root, run:

```bash
mkdir -p ~/.claude/skills
cp -r . ~/.claude/skills/tokenized-stock-tracking-analysis
```

After installation, Claude Code should automatically recognize the skill when you ask for tasks such as:

* Analyze MU vs MUon
* Analyze NVDA vs NVDAon
* Check tokenized stock tracking quality
* Compare a real U.S. stock with its Ondo tokenized stock equivalent
* Calculate premium/discount and return correlation for a tokenized stock

## Usage

### Full analysis

```bash
cd ~/.claude/skills/tokenized-stock-tracking-analysis
```

Run MU / MUon analysis:

```bash
python scripts/run_full_analysis.py \
  --stock-ticker MU \
  --coin-id micron-technology-ondo-tokenized-stock \
  --tokenized-symbol MUon \
  --output-dir ./MU_MUon_tracking
```

Run NVDA / NVDAon analysis:

```bash
python scripts/run_full_analysis.py \
  --stock-ticker NVDA \
  --coin-id nvidia-ondo-tokenized-stock \
  --tokenized-symbol NVDAon \
  --output-dir ./NVDA_NVDAon_tracking
```

### Step-by-step execution

Step 1: Fetch data

```bash
python scripts/fetch_data.py \
  --stock-ticker MU \
  --coin-id micron-technology-ondo-tokenized-stock \
  --output-dir ./output
```

Step 2: Align tokenized prices to U.S. market close

```bash
python scripts/align_us_close.py --input-dir ./output
```

Step 3: Analyze tracking quality

```bash
python scripts/analyze_tracking.py --input-dir ./output
```

Step 4: Generate charts

```bash
python scripts/plot_charts.py \
  --input-dir ./output \
  --stock-ticker MU \
  --tokenized-symbol MUon
```

## Output files

| File                                        | Description                                                            |
| ------------------------------------------- | ---------------------------------------------------------------------- |
| `raw_stock.csv`                             | Daily OHLCV data for the real U.S. stock                               |
| `raw_tokenized_price.csv`                   | Hourly or timestamped tokenized stock price data                       |
| `us_close_aligned.csv`                      | Tokenized prices aligned to New York 16:00 market close                |
| `tracking_analysis.csv`                     | Full tracking analysis dataset, including returns, NAV, and deviations |
| `tracking_summary.csv`                      | Summary of core tracking metrics                                       |
| `top_return_diff_dates.csv`                 | Top 10 dates with the largest return differences                       |
| `top_premium_discount_dates.csv`            | Top 10 dates with the largest premium/discount deviations              |
| `charts/01_nav_comparison.png`              | NAV comparison chart                                                   |
| `charts/02_return_scatter.png`              | Daily return scatter plot with regression line                         |
| `charts/03_return_diff_timeseries.png`      | Daily return difference time series                                    |
| `charts/04_premium_discount_timeseries.png` | Premium/discount time series                                           |
| `charts/05_premium_discount_histogram.png`  | Premium/discount distribution                                          |
| `chart_interpretation.md`                   | English interpretation report                                          |

## CoinGecko Coin IDs

| U.S. Stock | CoinGecko Coin ID                        |
| ---------- | ---------------------------------------- |
| MU         | `micron-technology-ondo-tokenized-stock` |
| NVDA       | `nvidia-ondo-tokenized-stock`            |

For other Ondo tokenized stocks, search CoinGecko for the relevant asset and use its CoinGecko coin ID.

## Why market-close alignment matters

Tokenized stocks trade 24/7, while U.S. stocks trade during regular market hours. A direct comparison between CoinGecko daily close prices and U.S. stock daily close prices can produce misleading results because the timestamps may not match.

This workflow aligns each tokenized stock price to the U.S. stock market close time, New York 16:00, before calculating returns, correlation, beta, tracking error, and premium/discount.

## Key metrics

The workflow calculates:

* Price correlation
* Pearson return correlation
* Spearman return correlation
* Regression alpha
* Regression beta
* R-squared
* Daily return difference
* Annualized tracking error
* Premium/discount
* NAV comparison
* Long-term tracking gap
* Largest deviation dates

## Notes

* CoinGecko free API access may be rate-limited.
* Historical data granularity may vary by asset and time range.
* Hourly tokenized stock data may not be available for all assets.
* The workflow measures price tracking only.
* It does not verify legal ownership, custody arrangements, redemption rights, issuer solvency, or regulatory status.
* Historical tracking quality does not guarantee future tracking quality.

## Risk disclaimer

This project is for research, educational, and analytical practice purposes only. It does not provide investment advice, financial advice, trading advice, legal advice, tax advice, or any recommendation to buy, sell, hold, or trade any asset.

Cryptocurrency, digital assets, tokenized stocks, and on-chain financial products involve significant risk. Prices can be highly volatile, liquidity can disappear quickly, platforms may restrict access, and users may lose part or all of their capital.

Tokenized stocks are not the same as real stocks. They may not provide shareholder rights, voting rights, dividend rights, direct ownership of the underlying equity, or the same regulatory protections available through traditional securities markets.

Tokenized stock products may involve additional risks, including but not limited to:

- issuer risk
- custody risk
- liquidity risk
- smart contract risk
- oracle or pricing risk
- platform or exchange risk
- blockchain network risk
- regulatory risk
- redemption risk
- delisting or trading suspension risk

This workflow only analyzes historical price-tracking behavior. It does not verify legal ownership, issuer solvency, reserve backing, custody arrangements, redemption rights, compliance status, or the enforceability of any claim against the issuer or underlying assets.

Historical tracking quality does not guarantee future tracking quality. A tokenized stock that tracked well in the past may diverge from the underlying stock in the future due to liquidity conditions, market stress, issuer issues, regulatory actions, exchange restrictions, or other events.

Users are solely responsible for their own research and decisions. Before interacting with tokenized stocks, cryptocurrencies, or any digital asset product, users should conduct independent due diligence and consult qualified professional advisers where appropriate.
