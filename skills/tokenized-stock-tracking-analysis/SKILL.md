---
name: tokenized-stock-tracking-analysis
description: Analyze tracking quality between a US stock and its Ondo tokenized stock equivalent. Handles NY 16:00 time alignment, return correlation, regression (beta/alpha/R²), premium/discount, tracking error, NAV comparison, basic analytical charts, and an English interpretation report. Use when the user asks to compare a real US equity such as NVDA, MU, or TSLA with an Ondo tokenized stock like NVDAon or MUon. Trigger keywords include: tokenized stock, Ondo tokenized stock, tracking analysis, premium discount, NAV comparison, on-chain stock vs real stock.
---

# Tokenized Stock Tracking Analysis

Analyze whether an Ondo tokenized stock (e.g., MUon, NVDAon) accurately tracks its underlying US-listed equity.

## When to Use This Skill

- Comparing MU vs MUon, NVDA vs NVDAon, or any US stock vs its Ondo tokenized stock
- Checking whether a tokenized stock can serve as a substitute price exposure
- Calculating return correlation between spot and tokenized assets
- Calculating premium/discount at NY market close
- Generating basic but clear analytical charts and an English interpretation report

## Core Principles

1. **Never use CoinGecko daily close directly.** Tokenized stocks trade 24/7 with no true daily close.
2. **Always align by NY 16:00.** For each US trading day, find the tokenized stock price closest to New York 16:00 (market close).
3. **Handle timezones correctly.** Use `America/New_York` via `zoneinfo`, which handles DST automatically.
4. **Quality-flag poor matches.** If the closest tokenized price is >90 minutes from NY 16:00, mark as `low_quality_match = True`.
5. **All return calculations use aligned prices.** `stock_return` from Adj Close, `tokenized_return` from the snapped price.
6. **For 1:1 tokenized stocks:** beta should ≈1, alpha ≈0, R² high.
7. **Always warn about risks.** Tokenized stocks ≠ real stocks. Highlight issuer, liquidity, platform, and regulatory risks.

## Required User Inputs

| Parameter | Description | Example |
|---|---|---|
| `stock_ticker` | Yahoo Finance ticker | `MU`, `NVDA` |
| `coin_id` | CoinGecko coin ID | `micron-technology-ondo-tokenized-stock` |
| `tokenized_symbol` | Display name for the tokenized stock | `MUon`, `NVDAon` |

Optional:
- `start_date` (default: earliest available)
- `end_date` (default: latest available)
- `output_dir` (default: `{stock}_{token}_tracking/`)

## Workflow

### Step 1: Create project folder

```
{output_dir}/
```

### Step 2: Fetch US stock data

Use Yahoo Finance chart API or yfinance. Fields: Date, Open, High, Low, Close, Adj Close, Volume. Save as `raw_stock.csv`.

### Step 3: Fetch tokenized stock data

Use CoinGecko `market_chart/range` in 30-day chunks to get ~1-hour granularity. Save as `raw_tokenized_price.csv` with fields: `ts_ms`, `datetime_utc`, `tokenized_price`.

### Step 4: Align by NY 16:00

For each US trading day:
- Construct NY 16:00 → convert to UTC
- Find the closest tokenized stock price
- If the time difference is greater than 90 minutes, mark the row as `low_quality_match = True`
- Record time difference and quality flag

Output: `us_close_aligned.csv`

### Step 5: Calculate returns

```
stock_return = Adj Close / lag(Adj Close) - 1
tokenized_return = tokenized_price / lag(tokenized_price) - 1
return_diff = tokenized_return - stock_return
```

### Step 6: Calculate premium/discount

```
premium_discount = tokenized_price_at_us_close / stock_adj_close - 1
```

### Step 7: Compute all metrics

See `tracking_summary.csv` for the full metric list.

### Step 8: Find top deviation dates

`top_return_diff_dates.csv`, `top_premium_discount_dates.csv`

### Step 9: Generate charts

5 basic but clear analytical charts saved to `charts/`. The charts prioritize accuracy and readability over visual embellishment, suitable for inclusion in reports or presentations.

### Step 10: Write interpretation report

Generate an English interpretation report.

Saved as `chart_interpretation.md`.

## Output Files

| File | Description |
|---|---|
| `raw_stock.csv` | US stock OHLCV |
| `raw_tokenized_price.csv` | Tokenized hourly price |
| `us_close_aligned.csv` | NY 16:00 aligned prices |
| `tracking_analysis.csv` | Full data with NAV, returns, return_diff |
| `tracking_summary.csv` | All core metrics |
| `top_return_diff_dates.csv` | Top 10 return diff dates |
| `top_premium_discount_dates.csv` | Top 10 P/D deviation dates |
| `charts/01_nav_comparison.png` | NAV comparison |
| `charts/02_return_scatter.png` | Return scatter + regression |
| `charts/03_return_diff_timeseries.png` | Daily return diff |
| `charts/04_premium_discount_timeseries.png` | P/D timeseries |
| `charts/05_premium_discount_histogram.png` | P/D distribution |
| `chart_interpretation.md` | Full English interpretation report |

## Interpretation Rules

| Criterion | Threshold | Interpretation |
|---|---|---|
| Pearson r | ≥ 0.95 | Daily returns highly synchronized |
| Beta | 0.95–1.05 | Close to 1:1 tracking |
| R² | ≥ 0.90 | High explanatory power |
| Mean P/D | Near 0 | No systematic premium/discount |
| Days in ±2% | > 95% | Good price alignment |
| P/D > ±5% | Any occurrence | Must flag as liquidity/abnormal risk |
| Long-term gap | Near 0 | NAV compound close to spot |

**Always state:** tokenized stock ≠ real stock, regardless of metrics.

## Limitations

- CoinGecko data availability and granularity may vary by asset. Hourly data may not be available for every asset or time range.
- The free CoinGecko API limits historical data to the past 365 days (`days=365`) via the `market_chart` endpoint; older hourly data may require the `market_chart/range` endpoint, which returns daily granularity for periods older than ~90 days.
- This analysis measures price tracking only. It does not verify legal ownership, custody, redemption rights, or issuer solvency.
- Historical tracking quality does not guarantee future tracking quality. Market conditions, liquidity profiles, and issuer operations can change.
- Tokenized stocks are not equivalent to real stocks. They do not confer voting rights, dividend entitlements, or the same regulatory protections.

## Disclaimer

This skill is for research, educational, and analytical practice purposes only. It does not provide investment advice, financial advice, trading advice, legal advice, tax advice, or any recommendation to buy, sell, hold, or trade any asset.

Cryptocurrency, digital assets, tokenized stocks, and on-chain financial products involve significant risk, including possible loss of capital.

Tokenized stocks are not the same as real stocks. They may not provide shareholder rights, voting rights, dividend rights, direct ownership of the underlying equity, or the same regulatory protections available through traditional securities markets.

This skill only analyzes historical price-tracking behavior. It does not verify legal ownership, issuer solvency, reserve backing, custody arrangements, redemption rights, compliance status, or the enforceability of any claim against the issuer or underlying assets.

This skill does not evaluate whether a tokenized stock is legally, operationally, or economically equivalent to the underlying equity.

Historical tracking quality does not guarantee future tracking quality. A tokenized stock that tracked well in the past may diverge from the underlying stock in the future due to liquidity conditions, market stress, issuer issues, regulatory actions, exchange restrictions, or other events.

Users are solely responsible for their own research and decisions.

## Dependencies

```
pandas, numpy, yfinance, requests, matplotlib, scipy, scikit-learn, python-dateutil, pytz
```
Python ≥3.9 required (for `zoneinfo`).
