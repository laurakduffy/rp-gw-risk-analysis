# GiveWell Cost-Effectiveness Risk Analysis

## Summary

This analysis applies the Rethink Priorities distribution fitting and risk analysis framework to GiveWell's preliminary cost-effectiveness estimates. The analysis evaluates three types of effects across six time horizons using nine different risk profiles.

## Input Data

Source: `Preliminary_GW_Cost-Effectiveness_Estimates_-_Percentiles_for_python.csv`

**Effect Types:**
1. **Life Years Saved** per $1M
2. **YLDs (Years Lived with Disability) Averted** per $1M  
3. **Income Doublings** per $1M

**Time Horizons:**
- t0: 0-5 years
- t1: 5-10 years
- t2: 10-20 years
- t3: 20-100 years
- t4: 100-500 years
- t5: 500+ years

## Methodology

### Distribution Generation
Given sparse percentile data (5th, mean, 95th), the analysis:
1. Estimates intermediate percentiles (p1, p10, p25, p50, p75, p90, p99) using geometric/arithmetic interpolation
2. Generates 10,000 samples using quantile interpolation
3. Applies risk adjustment models to the empirical distribution

### Risk Profiles

**Informal Adjustments:**
1. **Neutral**: Risk-neutral expected value (mean)
2. **Upside**: Truncates distribution at 99th percentile (skeptical of extreme upsides)
3. **Downside**: Loss-averse utility with λ=2.5 around median (amplifies losses)
4. **Combined**: Applies both truncation AND loss aversion

**Formal Models (Duffy 2023):**
5. **DMREU**: Difference-Making Risk-Weighted Expected Utility (p=0.05, moderate risk aversion)
6. **WLU - Low**: Weighted Linear Utility (c=0.01, minimal risk aversion)
7. **WLU - Moderate**: Weighted Linear Utility (c=0.05, moderate risk aversion)
8. **WLU - High**: Weighted Linear Utility (c=0.1, high risk aversion)
9. **Ambiguity Aversion**: Expected Difference Made with cubic weighting (k=4.0, mild aversion)

## Key Results

### Life Years Saved (0-5 year horizon)
- **Neutral EV**: 13,997 life-years/$1M
- **Upside Skeptical**: 13,950 (-0.3%)
- **Downside Critical**: 12,725 (-9.1%)
- **Combined**: 12,665 (-9.5%)
- **DMREU**: 13,076 (-6.6%)
- **WLU (moderate)**: 13,984 (-0.1%)
- **Ambiguity Aversion**: 13,557 (-3.1%)

The downside-critical and combined profiles show the largest reductions (~9-10%), reflecting strong loss aversion. DMREU provides intermediate risk adjustment (~7% reduction). WLU profiles remain closer to neutral, indicating lower sensitivity to distribution shape.

### YLDs Averted (0-5 year horizon)
- **Neutral EV**: 3,185 YLDs/$1M
- **Downside Critical**: 2,895 (-9.1%)
- **Combined**: 2,882 (-9.5%)

Similar risk adjustment patterns to life years saved.

### Income Doublings
All time horizons show zero values in the input data, so all risk profiles return zero.

## Interpretation

**Risk Aversion Impact:**
The formal risk models (DMREU, WLU, Ambiguity) show that:
- Accounting for risk preferences reduces the expected value by 0-7% depending on the model
- The informal downside-critical models show stronger effects (9-10% reduction)
- This suggests GiveWell's estimates are relatively robust to risk aversion, with moderate downside protection

**Time Horizon Pattern:**
Effects concentrate heavily in early horizons (0-20 years), with 100+ year horizons showing zero impact in the current estimates.

**Distribution Shape:**
The relatively small gap between risk-adjusted and neutral values suggests the underlying distributions are not highly skewed or heavy-tailed - the 5th to 95th percentile ranges are reasonably symmetric around the mean.

## Technical Notes

- Samples generated via piecewise linear quantile interpolation (no parametric distribution fit required)
- All risk models applied to the same empirical sample (10,000 draws)
- Loss aversion parameter λ=2.5 (standard Kahneman-Tversky value)
- DMREU parameter p=0.05 (moderate risk aversion per Duffy 2023)
- WLU concavity c ∈ {0.01, 0.05, 0.1} (low, moderate, high)
- Ambiguity cubic coefficient k=4.0 (mild aversion, 1.5x weight to worst)

## Output Format

The output CSV matches the RP format with:
- One row per effect type
- Columns: project_id, near_term_xrisk, effect_id, recipient_type
- 54 risk-adjusted value columns: (9 risk profiles) × (6 time horizons)

## References

- Duffy, Laura (2023). "Risk-Averse Effective Altruism". Rethink Priorities.
- Rethink Priorities Cross-Cause Cost-Effectiveness Model (CCM)
- RP Distribution Fitting Library (github.com/CharlesD353/rp-distribution-fitting)
