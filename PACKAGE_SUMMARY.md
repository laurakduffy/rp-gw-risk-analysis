# GiveWell Risk Analysis - Complete Package

## What You're Getting

A complete, standalone Python toolkit for running risk-adjusted cost-effectiveness analysis on GiveWell data.

### 📦 Package Contents (11 files)

#### Core Analysis Files
✓ **gw_risk_analysis.py** - Main script (run this)
✓ **risk_analysis.py** - Risk adjustment functions
✓ **requirements.txt** - Dependencies to install

#### Documentation
✓ **README.md** - Complete documentation (10KB)
✓ **QUICKSTART.md** - 5-minute getting started
✓ **MANIFEST.md** - File listing and relationships

#### Testing & Examples
✓ **test_setup.py** - Verify your setup works
✓ **example_input.csv** - Sample GiveWell data
✓ **gw_risk_analysis_output.csv** - Example output
✓ **gw_risk_analysis_summary.md** - Analysis interpretation

## 🚀 Quick Start (3 Steps)

### 1. Install (30 seconds)
```bash
pip install -r requirements.txt
```

### 2. Test (20 seconds)
```bash
python test_setup.py
```

### 3. Run (1-2 minutes)
```bash
python gw_risk_analysis.py example_input.csv my_results.csv --verbose
```

## 📊 What It Does

Takes sparse percentile data (5th, mean, 95th):
```
Life years saved/$1M: p5=10,134  mean=13,951  p95=18,242
```

Generates 10,000 samples and computes **9 risk profiles**:

| Profile | Example Value | Change |
|---------|---------------|--------|
| Neutral | 13,997 | - |
| Upside | 13,950 | -0.3% |
| Downside | 12,725 | -9.1% |
| Combined | 12,665 | -9.5% |
| DMREU | 13,076 | -6.6% |
| WLU (low) | 13,995 | -0.0% |
| WLU (moderate) | 13,984 | -0.1% |
| WLU (high) | 13,965 | -0.2% |
| Ambiguity | 13,557 | -3.1% |

## 🎯 Key Features

✅ **9 Risk Profiles** - Informal + formal models (Duffy 2023)
✅ **3 Effect Types** - Life years, YLDs, income doublings
✅ **6 Time Horizons** - 0-5yr through 500+ years
✅ **Deterministic** - Reproducible results (no random seed)
✅ **Fast** - Processes full dataset in ~2 seconds
✅ **Tested** - Built-in verification script
✅ **Documented** - 15KB of documentation

## 📋 Requirements

- Python 3.8 or higher
- numpy, pandas, scipy
- ~100KB disk space
- No internet connection needed after installation

## 🔧 Customization

All parameters are configurable in the script:

```python
# Risk aversion levels
DMREU_P = 0.05              # 0.01=neutral, 0.05=moderate, 0.10=high
WLU_MODERATE = 0.05         # 0.01=low, 0.05=moderate, 0.1=high
LOSS_AVERSION_LAMBDA = 2.5  # 1.0=none, 2.5=standard, 5.0=high

# Sampling
N_SAMPLES = 10000           # More samples = smoother but slower
```

## 📖 Documentation Included

1. **README.md** (10KB) - Everything you need:
   - Installation instructions
   - Usage examples
   - Complete methodology
   - Risk profile explanations
   - Customization guide
   - Troubleshooting

2. **QUICKSTART.md** (3.5KB) - Get running in 5 minutes

3. **MANIFEST.md** (3.4KB) - File structure and relationships

## ✅ Verification

Run the test script to verify everything works:

```bash
python test_setup.py
```

Expected output:
```
✓ ALL TESTS PASSED

You're ready to run the analysis!
```

## 📤 Input Format

Your CSV needs these sections:
- "Life years saved/$1M" with 6 time horizon rows
- "YLDs averted/$1M" with 6 time horizon rows  
- "Income Doublings/$1M" with 6 time horizon rows

Each row: `time_horizon, 5th_percentile, mean, 95th_percentile`

See `example_input.csv` for reference.

## 📥 Output Format

Standard RP format CSV with:
- 3 rows (one per effect type)
- 58 columns (4 metadata + 54 risk values)
- Risk values = 9 profiles × 6 time horizons

See `gw_risk_analysis_output.csv` for example.

## 🔬 Methodology

Based on **Duffy (2023)** "Risk-Averse Effective Altruism":

**Informal Models**:
- Upside skepticism (truncation)
- Loss aversion (Kahneman-Tversky)
- Combined adjustment

**Formal Models**:
- DMREU (probability weighting)
- WLU (outcome weighting)
- Ambiguity aversion (rank weighting)

All applied to empirical samples generated from percentiles.

## 💡 Use Cases

✓ Compare interventions under different risk preferences
✓ Sensitivity analysis on tail risk
✓ Portfolio optimization with risk constraints
✓ Robustness checks for cost-effectiveness estimates
✓ Research on risk aversion in EA decision-making

## 📚 References

1. Duffy, Laura (2023). "Risk-Averse Effective Altruism". Rethink Priorities.
2. Kahneman & Tversky (1979). "Prospect Theory".
3. RP Cross-Cause Cost-Effectiveness Model.

## 🆘 Support

Check documentation in order:
1. **QUICKSTART.md** - Common issues
2. **README.md** - Full documentation
3. **Code comments** - Implementation details
4. **Duffy (2023)** - Theoretical background

## ⚖️ License

Based on Rethink Priorities framework. Please cite appropriately.

---

## Ready to Go!

```bash
# 1. Install
pip install -r requirements.txt

# 2. Test  
python test_setup.py

# 3. Run
python gw_risk_analysis.py your_input.csv results.csv --verbose
```

**Questions?** → Check README.md
**Issues?** → Run test_setup.py
**Examples?** → See example_input.csv and gw_risk_analysis_output.csv

---

Created: 2026-03-06  
Version: 1.0  
Package Size: ~105KB (11 files)
