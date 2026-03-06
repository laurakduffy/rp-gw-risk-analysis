# GiveWell Cost-Effectiveness Risk Analysis

Python toolkit for applying risk-adjusted analysis to GiveWell cost-effectiveness estimates using the Rethink Priorities framework.

## Overview

This toolkit processes GiveWell's cost-effectiveness percentile data through multiple risk adjustment models, generating risk-adjusted expected values under nine different risk preference profiles.

**Input**: Sparse percentile data (5th, mean, 95th) for three effect types across six time horizons

**Output**: Risk-adjusted values for all combinations of:
- 9 risk profiles (neutral, upside, downside, combined, DMREU, 3×WLU, ambiguity)
- 3 effect types (life years saved, YLDs averted, income doublings)
- 6 time horizons (0-5yr, 5-10yr, 10-20yr, 20-100yr, 100-500yr, 500+yr)

## Installation

### Requirements
- Python 3.8+
- pip

### Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Verify installation**:
```bash
python gw_risk_analysis.py --help
```

## Usage

### Basic Usage

```bash
python gw_risk_analysis.py input.csv output.csv
```

### With Verbose Output

```bash
python gw_risk_analysis.py input.csv output.csv --verbose
```

### Example

```bash
python gw_risk_analysis.py \
    Preliminary_GW_Cost-Effectiveness_Estimates_-_Percentiles_for_python.csv \
    gw_risk_adjusted_output.csv \
    --verbose
```

## Input Format

The input CSV should have this structure:

```
Life years saved/$1M,5th-percentile,Mean,95th percentile
0-5 years,10134.48,13951.36,18242.07
5-10 years,788.24,1085.11,1418.83
...

YLDs averted/$1M,5th-percentile,Mean,95th percentile
0-5 years,2305.81,3174.23,4150.46
...

Income Doublings/$1M,5th-percentile,Mean,95th percentile
0-5 years,0.00,0.00,0.00
...
```

**Key requirements**:
- Section headers containing: "life years saved", "ylds averted", or "income doublings"
- Time horizon labels: "0-5 years", "5-10 years", "10-20 years", "20-100 years", "100-500 years", "500+ years"
- Three data columns: 5th percentile, mean, 95th percentile

## Output Format

The output CSV follows the Rethink Priorities standard format:

```
project_id,near_term_xrisk,effect_id,recipient_type,neutral_t0,neutral_t1,...
givewell,FALSE,life_years_saved,life_years,13997.43,1088.69,...
givewell,FALSE,ylds_averted,ylds,3184.71,247.70,...
givewell,FALSE,income_doublings,income_doublings,0.0,0.0,...
```

**Columns**:
- `project_id`: Always "givewell"
- `near_term_xrisk`: Always "FALSE" 
- `effect_id`: Effect type (life_years_saved, ylds_averted, income_doublings)
- `recipient_type`: Simplified effect type for categorization
- `{risk_profile}_t{0-5}`: 54 columns with risk-adjusted values

**Risk profile column prefixes**:
- `neutral_t*`: Risk-neutral expected value
- `upside_t*`: Upside-skeptical (truncated at p99)
- `downside_t*`: Downside-critical (loss aversion λ=2.5)
- `combined_t*`: Both truncation and loss aversion
- `dmreu_t*`: Difference-Making Risk-Weighted EU (p=0.05)
- `wlu - low_t*`: Weighted Linear Utility (c=0.01)
- `wlu - moderate_t*`: Weighted Linear Utility (c=0.05)
- `wlu - high_t*`: Weighted Linear Utility (c=0.1)
- `ambiguity_t*`: Ambiguity aversion (k=4.0)

**Time horizon suffixes**:
- `_t0`: 0-5 years
- `_t1`: 5-10 years
- `_t2`: 10-20 years
- `_t3`: 20-100 years
- `_t4`: 100-500 years
- `_t5`: 500+ years

## Methodology

### Distribution Generation

Given sparse percentiles (p5, mean, p95), the analysis:

1. **Estimates intermediate percentiles** using geometric interpolation for log-normal-shaped distributions:
   - p50 ≈ √(p5 × p95)
   - p1, p10, p25, p75, p90, p99 via geometric spacing

2. **Generates 10,000 samples** via quantile interpolation:
   - Creates uniform quantile points from 0.001 to 0.999
   - Interpolates values from the percentile curve
   - Produces deterministic empirical distribution

3. **Applies risk adjustments** to the empirical samples

### Risk Profiles

#### Informal Adjustments

**1. Neutral (Risk-Neutral EV)**
- Standard expected value: E[X]
- Mean of all samples
- No risk adjustment

**2. Upside (Upside Skepticism)**
- Truncates distribution at 99th percentile
- E[X | X ≤ p99]
- Discounts extreme positive outliers

**3. Downside (Loss Aversion)**
- Applies piecewise linear utility around median
- u(x) = x - ref for gains
- u(x) = λ(x - ref) for losses (λ=2.5)
- Amplifies downside risk

**4. Combined (Truncation + Loss Aversion)**
- Both upside truncation AND loss aversion
- Most conservative informal model

#### Formal Models (Duffy 2023)

**5. DMREU (Difference-Making Risk-Weighted Expected Utility)**
- Ranks outcomes worst-to-best
- Applies probability weighting: m(P) = P^a
- Parameter: p=0.05 → a≈1.54 (moderate risk aversion)
- Formula: Σ d_i × [m(P_i) - m(P_{i+1})]

**6. WLU - Low (Weighted Linear Utility, c=0.01)**
- Weights outcomes inversely by magnitude
- w(x) = 1/(1 + x^c) for x ≥ 0
- Minimal risk aversion

**7. WLU - Moderate (Weighted Linear Utility, c=0.05)**
- Moderate risk aversion
- Standard parameter choice

**8. WLU - High (Weighted Linear Utility, c=0.1)**
- High risk aversion
- Strong downside protection

**9. Ambiguity Aversion (k=4.0)**
- Cubic weighting of ranked outcomes
- w(i) = (1/N) × (-k(i/(N-1) - 0.5)³ + 1)
- Overweights worst outcomes, underweights best
- k=4.0 → mild aversion (range [0.5, 1.5])

### Parameters

Default values (can be modified in `gw_risk_analysis.py`):

```python
# Risk profile parameters
DMREU_P = 0.05              # moderate risk aversion
WLU_LOW = 0.01              # low risk aversion
WLU_MODERATE = 0.05         # moderate risk aversion
WLU_HIGH = 0.1              # high risk aversion
AMBIGUITY_K = 4.0           # mild ambiguity aversion

# Informal model parameters
TRUNCATION_PERCENTILE = 0.99
LOSS_AVERSION_LAMBDA = 2.5

# Sampling
N_SAMPLES = 10000
```

## File Structure

```
.
├── gw_risk_analysis.py      # Main analysis script
├── risk_analysis.py          # Risk adjustment functions (from RP)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── [your_input.csv]         # Input data (not included)
```

## Example Output

For Life Years Saved (0-5 year horizon):

| Risk Profile | Value | Change from Neutral |
|--------------|-------|---------------------|
| Neutral | 13,997 | - |
| Upside | 13,950 | -0.3% |
| Downside | 12,725 | -9.1% |
| Combined | 12,665 | -9.5% |
| DMREU | 13,076 | -6.6% |
| WLU (low) | 13,995 | -0.0% |
| WLU (moderate) | 13,984 | -0.1% |
| WLU (high) | 13,965 | -0.2% |
| Ambiguity | 13,557 | -3.1% |

**Interpretation**: 
- Loss aversion models (downside, combined) show the strongest effects (-9-10%)
- Formal risk models show moderate effects (-0 to -7%)
- Suggests relatively symmetric distributions without heavy tails

## Technical Notes

### Distribution Shape Assumptions

The analysis assumes log-normal-ish distributions when all values are positive, falling back to linear interpolation when zeros are present. This works well for cost-effectiveness data with:
- Moderate uncertainty (5th to 95th range spans 1.5-2× the median)
- Positive skew typical of cost-effectiveness distributions
- No extreme outliers

### Sampling Determinism

The sample generation is **deterministic** (not random):
- Samples at fixed quantile points via `np.linspace(0.001, 0.999, 10000)`
- Ensures reproducible results
- No random seed needed

### Limitations

1. **Sparse Percentile Data**: Only three input percentiles means estimated intermediate percentiles may not capture complex distribution shapes
2. **No Correlation Modeling**: Time horizons treated independently
3. **No Moral Weights**: Values are in original units (life-years, YLDs, income doublings)
4. **Point-in-Time**: No time discounting applied across horizons

## Customization

### Changing Risk Parameters

Edit the configuration section in `gw_risk_analysis.py`:

```python
# More aggressive loss aversion
LOSS_AVERSION_LAMBDA = 5.0

# More risk-averse DMREU
DMREU_P = 0.01  # instead of 0.05

# More samples for smoother distributions
N_SAMPLES = 50000
```

### Adding Custom Risk Profiles

Add your own risk adjustment function in the `compute_all_risk_profiles()` function:

```python
def compute_all_risk_profiles(draws):
    # ... existing code ...
    
    # Custom: exponential utility
    custom = float(np.mean(1 - np.exp(-draws / scale)))
    
    return {
        # ... existing profiles ...
        'custom': custom,
    }
```

Don't forget to add the column name to `write_output_csv()`.

## Troubleshooting

### Import Error: risk_analysis.py not found
**Solution**: Ensure `risk_analysis.py` is in the same directory as `gw_risk_analysis.py`

### ModuleNotFoundError: numpy/pandas/scipy
**Solution**: Run `pip install -r requirements.txt`

### Empty output or missing effects
**Solution**: Check that your input CSV has the correct section headers:
- "Life years saved" or "life years saved"
- "YLDs averted" or "ylds averted"  
- "Income Doublings" or "income doublings"

### Values seem wrong
**Solution**: Verify your input CSV has:
- Numeric values in columns 2-4 (5th percentile, mean, 95th percentile)
- Time horizon labels match exactly: "0-5 years", "5-10 years", etc.

## References

1. **Duffy, Laura (2023)**. "Risk-Averse Effective Altruism". Rethink Priorities.
   - DMREU, WLU, and Ambiguity Aversion models

2. **Rethink Priorities Cross-Cause Cost-Effectiveness Model (CCM)**
   - Framework for comparative cost-effectiveness analysis

3. **Kahneman & Tversky (1979)**. "Prospect Theory: An Analysis of Decision under Risk"
   - Loss aversion utility function

## License

Based on Rethink Priorities risk analysis framework. Please cite appropriately if used in research or publications.

## Contact

For questions about:
- **Methodology**: Refer to Duffy (2023) and Rethink Priorities documentation
- **Implementation**: Check code comments in `gw_risk_analysis.py` and `risk_analysis.py`
- **GiveWell data**: Contact GiveWell directly

## Version History

- **v1.0** (2026-03-06): Initial release
  - 9 risk profiles
  - 3 effect types × 6 time horizons
  - Sparse percentile input support
