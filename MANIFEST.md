# GiveWell Risk Analysis Package - File Manifest

## Core Files (Required)

### gw_risk_analysis.py
**Purpose**: Main analysis script  
**Size**: ~500 lines  
**Usage**: `python gw_risk_analysis.py input.csv output.csv`  
**Contains**:
- Data parsing functions
- Sample generation from percentiles
- Risk profile computation
- Output writing
- Command-line interface

### risk_analysis.py
**Purpose**: Risk adjustment functions (from Rethink Priorities)  
**Size**: ~550 lines  
**Usage**: Imported by main script  
**Contains**:
- `compute_dmreu()` - DMREU calculation
- `compute_wlu()` - Weighted Linear Utility
- `compute_ambiguity_aversion()` - Ambiguity aversion
- Supporting utility functions
- Integration and sampling helpers

### requirements.txt
**Purpose**: Python package dependencies  
**Contents**:
```
numpy>=1.24.0
pandas>=1.5.0
scipy>=1.10.0
```

## Documentation Files

### README.md
**Purpose**: Comprehensive documentation  
**Sections**:
- Overview and installation
- Usage examples
- Input/output formats
- Methodology details
- Risk profile descriptions
- Customization guide
- Troubleshooting
- References

### QUICKSTART.md
**Purpose**: 5-minute getting started guide  
**Sections**:
- Quick setup instructions
- Running your first analysis
- Interpreting results
- Common issues

## Testing & Examples

### test_setup.py
**Purpose**: Verify installation and setup  
**Usage**: `python test_setup.py`  
**Tests**:
- Module imports
- Risk functions
- Sample generation
- Full pipeline (if example file present)

### example_input.csv
**Purpose**: Example GiveWell percentile data  
**Format**: Same format required for all inputs  
**Contents**:
- Life years saved (6 time horizons)
- YLDs averted (6 time horizons)
- Income doublings (6 time horizons)

## Output Files (Generated)

### gw_risk_analysis_output.csv
**Purpose**: Example output from running the analysis  
**Format**: RP standard format with 58 columns  
**Contents**: Risk-adjusted values for all effect types

### gw_risk_analysis_summary.md
**Purpose**: Analysis summary and interpretation  
**Contents**:
- Key results
- Interpretation guide
- Technical notes
- Methodology summary

## File Relationships

```
User runs:
    gw_risk_analysis.py (main script)
        ↓
    Imports: risk_analysis.py (functions)
        ↓
    Reads: [user_input].csv (data)
        ↓
    Writes: [user_output].csv (results)

User tests:
    test_setup.py (verification)
        ↓
    Uses: example_input.csv (optional)
        ↓
    Tests all components
```

## Installation Checklist

- [ ] All core files in same directory
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test script passes (`python test_setup.py`)
- [ ] Ready to run analysis!

## Minimum Required Files

To run the analysis, you absolutely need:
1. `gw_risk_analysis.py`
2. `risk_analysis.py`
3. `requirements.txt` (for installation)
4. Your input CSV file

Documentation files (README.md, QUICKSTART.md) are helpful but optional.

## File Sizes

```
gw_risk_analysis.py      ~40 KB
risk_analysis.py         ~30 KB
README.md                ~20 KB
QUICKSTART.md            ~5 KB
requirements.txt         ~1 KB
test_setup.py            ~8 KB
example_input.csv        ~1 KB
```

**Total package size**: ~105 KB

## Version

Package version: 1.0  
Created: 2026-03-06  
Based on: Rethink Priorities risk analysis framework (Duffy 2023)
