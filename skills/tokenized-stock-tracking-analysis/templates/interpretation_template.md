# {stock_ticker} vs {tokenized_symbol} — Tracking Analysis Interpretation

**Sample period:** {sample_start_date} to {sample_end_date}
**Alignment method:** Tokenized price snapped to NY 16:00 market close
**Sample size:** {sample_size} trading days

## (1) Overall assessment

The tracking relationship between {tokenized_symbol} and {stock_ticker} is generally {strength}.
After NY 16:00 time alignment, the daily return Pearson correlation is {pearson_r}
(Spearman: {spearman_r}), the linear regression beta is {beta} ({beta_judgment}),
and R² is {r_squared}.

The annualized tracking error is {ann_te}%.
The mean premium/discount is {mean_pd}, with {within_2pct}% of trading days within ±2%.
Over the full period, {stock_ticker} returned {stock_cum}% and {tokenized_symbol} returned
{token_cum}%, for a long-term gap of {long_gap}.

Conclusion: When aligned to the U.S. market close, {tokenized_symbol} {can_serve_as} {stock_ticker}'s substitute price exposure.

## (2) Chart 1: NAV comparison

The NAV curves of {stock_ticker} (blue) and {tokenized_symbol} (red) {nav_overlap}.
The long-term gap of {long_gap} {long_gap_interpretation}.

## (3) Chart 2: Return scatter

Data points {distribution_desc} around the y=x reference line.
The regression line {regression_closeness} to y=x.
Pearson r = {pearson_r} and R² = {r_squared} indicate that approximately {explained_pct}%
of {tokenized_symbol}'s daily variance is explained by {stock_ticker}.
This {strongly_support} "{tokenized_symbol} serves as a practical substitute for {stock_ticker}."

## (4) Chart 3: Daily return difference

Daily return deviations of {tokenized_symbol} relative to {stock_ticker} are {diff_judgment}.
Mean: {mean_rd}, standard deviation: {std_rd}%.
Annualized tracking error: {ann_te}%.
Max positive deviation: {max_pos_rd}%, max negative deviation: {max_neg_rd}%.

## (5) Chart 4: Premium/discount time series

Mean premium/discount: {mean_pd}, no systematic premium or discount over the long term.
Max premium: {max_prem}%, max discount: {max_disc}%.
{extreme_pd_warning}

## (6) Chart 5: Premium/discount distribution

The premium/discount distribution is {concentration} concentrated,
with {within_2pct}% of trading days within ±2%.

## (7) Risk disclosures

1. **Not a real stock.** {tokenized_symbol} is an Ondo Finance-issued on-chain token.
   Holders do not possess legal ownership, voting rights, or dividend entitlements.
2. **Issuer risk.** Value depends on Ondo's redemption and custody mechanisms.
3. **Liquidity risk.** Volume may be low initially and during extreme conditions.
4. **Platform risk.** Network congestion, gas spikes, and cross-chain bridge risks.
5. **Regulatory / delisting risk.** Tokenized stock regulatory status is uncertain.
6. **Early-period extreme deviation risk.** {extreme_deviation_detail}

## (8) Final judgment

When aligned to the U.S. market close (NY 16:00), {tokenized_symbol} can serve as a
reasonable substitute price exposure for {stock_ticker}, but it is not equivalent to
owning the real stock. The full-sample results show {tracking_quality} tracking quality.
{early_stage_warning} Ongoing attention to liquidity, issuer, platform, and regulatory
risks is warranted for any long-term holding.
