# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies (30 seconds)
```bash
pip install -r requirements.txt
```

### 2. Verify Installation (10 seconds)
```bash
python gw_risk_analysis.py --help
```

You should see:
```
usage: gw_risk_analysis.py [-h] [-v] input_csv output_csv

GiveWell Cost-Effectiveness Risk Analysis
...
```

### 3. Run Analysis (1-2 minutes)
```bash
python gw_risk_analysis.py \
    your_input_file.csv \
    results.csv \
    --verbose
```

### 4. View Results (1 minute)
```bash
# Open in Excel, Google Sheets, or any CSV viewer
# Or use Python/pandas:
python -c "import pandas as pd; print(pd.read_csv('results.csv'))"
```

## What You'll Get

**Output file**: `results.csv` with 3 rows (one per effect type):
- Life years saved per $1M
- YLDs averted per $1M  
- Income doublings per $1M

**58 columns per row**:
- 4 metadata columns (project_id, near_term_xrisk, effect_id, recipient_type)
- 54 risk-adjusted value columns = 9 risk profiles × 6 time horizons

## Interpreting Results

### Example: Life Years Saved (0-5 years)

If you see these values in the CSV:
- `neutral_t0`: 13,997
- `downside_t0`: 12,725
- `dmreu_t0`: 13,076

**Interpretation**:
- **Neutral (13,997)**: Standard expected value, no risk adjustment
- **Downside (12,725)**: With loss aversion, value drops 9.1% → strong downside protection
- **DMREU (13,076)**: With moderate risk aversion, value drops 6.6% → balanced adjustment

The **gap between risk profiles** tells you:
- **Small gap (<5%)**: Distribution is relatively symmetric, low tail risk
- **Large gap (>10%)**: Heavy-tailed or skewed distribution, high uncertainty

### Key Questions to Ask

1. **Which risk profile should I use?**
   - Conservative: Use `downside` or `combined`
   - Balanced: Use `dmreu` or `wlu - moderate`
   - Aggressive: Use `neutral` or `wlu - low`

2. **Are effects robust to risk preferences?**
   - Check if all profiles are within 10% of neutral
   - If yes → robust, distribution is well-behaved
   - If no → sensitive to tail risk, investigate further

3. **Which time horizons matter?**
   - Compare `_t0` (0-5yr) vs `_t3` (20-100yr) vs `_t5` (500+yr)
   - Near-term dominated? Most value in t0-t2
   - Long-term dominated? Significant value in t3-t5

## Common Issues

### "ModuleNotFoundError: No module named 'risk_analysis'"
**Fix**: Make sure `risk_analysis.py` is in the same folder as `gw_risk_analysis.py`

### "FileNotFoundError: [Errno 2] No such file or directory"
**Fix**: Check your input file path. Use absolute path if needed:
```bash
python gw_risk_analysis.py \
    /full/path/to/input.csv \
    /full/path/to/output.csv
```

### Output has zeros for some effects
**Normal**: If your input CSV has zeros (e.g., income doublings), output will also be zero

### Values seem too high/low
**Check**: Make sure your input has the right units:
- Life years should be per $1M (not per $1000)
- Values in thousands to tens of thousands are normal

## Next Steps

1. **Read the full README.md** for detailed methodology
2. **Modify parameters** in `gw_risk_analysis.py` if needed
3. **Compare across interventions** by running on multiple datasets
4. **Visualize results** using your favorite plotting tool

## Need Help?

1. Check the **full README.md** for detailed documentation
2. Look at **code comments** in `gw_risk_analysis.py`
3. Review the **Duffy (2023) paper** for theoretical background

---

**Ready?** Run your first analysis now:
```bash
python gw_risk_analysis.py input.csv output.csv --verbose
```
