"""
GiveWell Cost-Effectiveness Risk Analysis
==========================================

Processes GiveWell cost-effectiveness percentile data through risk analysis pipeline.
Generates samples from sparse percentiles and computes 9 different risk profiles.

Usage:
    python gw_risk_analysis.py input.csv output.csv
    python gw_risk_analysis.py --help

Author: Based on Rethink Priorities risk analysis framework
"""

import sys
import csv
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

# Import risk analysis functions (from uploaded risk_analysis.py)
try:
    from risk_analysis import (
        compute_dmreu,
        compute_wlu,
        compute_ambiguity_aversion,
    )
except ImportError:
    print("ERROR: risk_analysis.py not found in the same directory.")
    print("Please ensure risk_analysis.py is in the same folder as this script.")
    sys.exit(1)


# ============================================================================
# CUSTOM AMBIGUITY AVERSION (PERCENTILE-BASED WEIGHTING)
# ============================================================================

def compute_ambiguity_aversion_percentile(samples: np.ndarray) -> float:
    """Percentile-Based Weighting for upside skepticism.

    Applies exponential decay to extreme positive outcomes:
    - X in [0, 97.5 percentile]: weight = 1.0
    - X in (97.5, 99.9 percentile]: weight = exp(-ln(100)/1.5 * (percentile - 97.5))
    - X >= 99.9 percentile: weight = 0.0
    
    Final weights normalized to sum to N for weighted mean calculation.
    
    Args:
        samples: np.ndarray of outcome values
        
    Returns:
        Weighted mean (float)
    """
    d = np.sort(samples)  # worst to best
    N = len(d)
    
    # Calculate percentile for each sample (0 to 100 scale)
    percentiles = np.arange(N) / (N - 1) * 100
    
    # Initialize preliminary weights
    prelim_weights = np.ones(N)
    
    # Apply exponential decay for (97.5, 99.9] percentile range
    mask_decay = (percentiles > 97.5) & (percentiles <= 99.9)
    if np.any(mask_decay):
        x = percentiles[mask_decay]
        decay_coef = -np.log(100) / 1.5  # ≈ -3.07
        prelim_weights[mask_decay] = np.exp(decay_coef * (x - 97.5))
    
    # Zero weight for samples above 99.9th percentile
    mask_zero = percentiles > 99.9
    prelim_weights[mask_zero] = 0.0
    
    # Normalize weights so they sum to N (for weighted mean)
    w_sum = np.sum(prelim_weights)
    if w_sum <= 0:
        return float(np.mean(samples))
    
    final_weights = prelim_weights * (N / w_sum)
    
    # Weighted mean: sum(weights * values) / N
    return float(np.sum(final_weights * d) / N)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Time horizon mapping (indices for output columns)
TIME_HORIZONS = {
    "0-5 years": 0,
    "5-10 years": 1,
    "10-20 years": 2,
    "20-100 years": 3,
    "100-500 years": 4,
    "500+ years": 5,
}

# Risk profile parameters (Duffy 2023)
DMREU_P = 0.05          # moderate risk aversion
WLU_LOW = 0.01          # low risk aversion
WLU_MODERATE = 0.05     # moderate risk aversion
WLU_HIGH = 0.1          # high risk aversion
AMBIGUITY_K = 4.0       # mild ambiguity aversion

# Informal model parameters
TRUNCATION_PERCENTILE = 0.99
LOSS_AVERSION_LAMBDA = 2.5

# Sampling parameters
N_SAMPLES = 10000


# ============================================================================
# DATA PARSING
# ============================================================================

def parse_gw_csv(filepath):
    """Parse the GiveWell CSV and extract effect data.
    
    Expected format:
        Row with "Life years saved/$1M" or similar headers
        Following rows: time_horizon, 5th-percentile, Mean, 95th-percentile
        
    Returns:
        dict with structure:
        {
            'life_years_saved': {
                '0-5 years': {'p5': float, 'mean': float, 'p95': float},
                ...
            },
            'ylds_averted': {...},
            'income_doublings': {...}
        }
    """
    df = pd.read_csv(filepath, header=None)
    
    data = {
        'life_years_saved': {},
        'ylds_averted': {},
        'income_doublings': {},
    }
    
    # Find the starting rows for each effect type
    effect_sections = {
        'life_years_saved': None,
        'ylds_averted': None,
        'income_doublings': None,
    }
    
    for idx, row in df.iterrows():
        cell = str(row[0]).lower()
        if 'life years saved' in cell:
            effect_sections['life_years_saved'] = idx
        elif 'ylds averted' in cell or 'yld' in cell:
            effect_sections['ylds_averted'] = idx
        elif 'income doublings' in cell or 'income' in cell:
            effect_sections['income_doublings'] = idx
    
    # Extract data for each section
    for effect_name, start_row in effect_sections.items():
        if start_row is None:
            continue
        
        # Parse the 6 time horizon rows following the header
        for i in range(6):
            data_row_idx = start_row + 1 + i
            if data_row_idx >= len(df):
                break
            
            row = df.iloc[data_row_idx]
            time_horizon = str(row[0]).strip()
            
            if time_horizon not in TIME_HORIZONS:
                continue
            
            # Extract percentiles (columns: time_horizon, 5th, mean, 95th)
            try:
                p5 = float(row[1])
                mean = float(row[2])
                p95 = float(row[3])
                
                data[effect_name][time_horizon] = {
                    'p5': p5,
                    'mean': mean,
                    'p95': p95,
                }
            except (ValueError, IndexError):
                continue
    
    return data


# ============================================================================
# DISTRIBUTION GENERATION
# ============================================================================

def generate_samples_from_percentiles(p5, mean, p95, n_samples=N_SAMPLES):
    """Generate samples from three percentiles using piecewise linear CDF.
    
    Creates a distribution that:
    - Has 5% of mass below p5
    - Has estimated median around geometric/arithmetic mean of p5 and p95
    - Has 5% of mass above p95
    
    Args:
        p5: 5th percentile value
        mean: Mean value (for reference)
        p95: 95th percentile value
        n_samples: Number of samples to generate
        
    Returns:
        np.ndarray of samples
    """
    if p5 == 0 and mean == 0 and p95 == 0:
        return np.zeros(n_samples)
    
    # Estimate additional percentiles for better distribution shape
    if p5 > 0 and p95 > 0:
        # Estimate median from geometric mean of p5 and p95 (log-normal shape)
        p50 = np.sqrt(p5 * p95)
        
        # Estimate other percentiles via geometric extrapolation/interpolation
        p1 = p5 * (p5 / p50) ** (4/45)
        p10 = p5 * (p50 / p5) ** (5/45)
        p25 = p10 * (p50 / p10) ** (15/25)
        p75 = p50 * (p95 / p50) ** (25/45)
        p90 = p50 * (p95 / p50) ** (40/45)
        p99 = p95 * (p95 / p50) ** (4/45)
    else:
        # Linear interpolation fallback for cases with zeros
        p50 = (p5 + p95) / 2
        p1 = p5 * 0.5
        p10 = p5 + 0.05/0.45 * (p50 - p5)
        p25 = p5 + 0.20/0.45 * (p50 - p5)
        p75 = p50 + 0.25/0.45 * (p95 - p50)
        p90 = p50 + 0.40/0.45 * (p95 - p50)
        p99 = p95 + (p95 - p50) * 0.1
    
    # Create quantile points and values
    quantiles = np.array([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99])
    values = np.array([p1, p5, p10, p25, p50, p75, p90, p95, p99])
    
    # Generate uniform quantile points and interpolate
    sample_quantiles = np.linspace(0.001, 0.999, n_samples)
    samples = np.interp(sample_quantiles, quantiles, values)
    
    return samples


# ============================================================================
# RISK PROFILE COMPUTATION
# ============================================================================

def compute_all_risk_profiles(draws):
    """Compute all 9 risk profiles from empirical draws.
    
    Args:
        draws: np.ndarray of outcome samples
        
    Returns:
        dict with keys: neutral, upside, downside, combined, dmreu,
                       wlu_low, wlu_moderate, wlu_high, ambiguity
                       
    Note:
        Ambiguity profile uses percentile-based weighting:
        - Full weight (1.0) for outcomes ≤ 97.5th percentile
        - Exponential decay from 97.5th to 99.9th percentile
        - Zero weight for outcomes > 99.9th percentile
    """
    draws = np.asarray(draws, dtype=float)
    
    # ========================================================================
    # INFORMAL ADJUSTMENTS
    # ========================================================================
    
    # 1. Neutral: risk-neutral expected value (mean)
    neutral = float(np.mean(draws))
    
    # 2. Upside: truncate at 99th percentile (skeptical of extreme upsides)
    trunc_val = np.percentile(draws, TRUNCATION_PERCENTILE * 100)
    mask = draws <= trunc_val
    upside = float(np.mean(draws[mask]))
    
    # 3. Downside: loss-averse utility around median reference point
    ref = float(np.median(draws))
    gains = draws - ref
    utilities = np.where(gains >= 0, gains, LOSS_AVERSION_LAMBDA * gains)
    downside = float(np.mean(utilities) + ref)
    
    # 4. Combined: truncation + loss aversion applied together
    truncated = draws[mask]
    gains_t = truncated - ref
    utilities_t = np.where(gains_t >= 0, gains_t, LOSS_AVERSION_LAMBDA * gains_t)
    combined = float(np.mean(utilities_t) + ref)
    
    # ========================================================================
    # FORMAL MODELS (Duffy 2023)
    # ========================================================================
    
    # 5. DMREU: Difference-Making Risk-Weighted Expected Utility
    dmreu = compute_dmreu(fit=None, p=DMREU_P, samples=draws)
    
    # 6-8. WLU: Weighted Linear Utility (three levels of risk aversion)
    wlu_low = compute_wlu(fit=None, c=WLU_LOW, samples=draws)
    wlu_moderate = compute_wlu(fit=None, c=WLU_MODERATE, samples=draws)
    wlu_high = compute_wlu(fit=None, c=WLU_HIGH, samples=draws)
    
    # 9. Ambiguity Aversion: percentile-based weighting
    #    (downweights outcomes above 97.5th percentile exponentially)
    ambiguity = compute_ambiguity_aversion_percentile(samples=draws)
    
    return {
        'neutral': neutral,
        'upside': upside,
        'downside': downside,
        'combined': combined,
        'dmreu': dmreu,
        'wlu_low': wlu_low,
        'wlu_moderate': wlu_moderate,
        'wlu_high': wlu_high,
        'ambiguity': ambiguity,
    }


# ============================================================================
# OUTPUT WRITING
# ============================================================================

def write_output_csv(results, output_path, verbose=False):
    """Write results in the RP output format.
    
    Format:
        - One row per effect type
        - Columns: project_id, near_term_xrisk, effect_id, recipient_type
        - 54 risk-adjusted value columns: (9 risk profiles) × (6 time horizons)
    
    Args:
        results: list of result dicts
        output_path: path to write CSV
        verbose: print summary info
    """
    # Group results by effect type
    by_effect = {}
    for r in results:
        effect_type = r['effect_type']
        if effect_type not in by_effect:
            by_effect[effect_type] = []
        by_effect[effect_type].append(r)
    
    # Build output rows
    output_rows = []
    
    risk_profile_names = [
        'neutral', 'upside', 'downside', 'combined', 'dmreu',
        'wlu_low', 'wlu_moderate', 'wlu_high', 'ambiguity'
    ]
    
    for effect_type, effect_results in by_effect.items():
        # Sort by time index
        effect_results.sort(key=lambda x: x['time_idx'])
        
        # Build row
        row = {
            'project_id': 'givewell',
            'near_term_xrisk': 'FALSE',
            'effect_id': effect_type,
            'recipient_type': effect_results[0]['recipient_type'],
        }
        
        # Add columns for each risk profile and time horizon
        for rp_name in risk_profile_names:
            # Map to output column names
            rp_display = {
                'neutral': 'neutral',
                'upside': 'upside',
                'downside': 'downside',
                'combined': 'combined',
                'dmreu': 'dmreu',
                'wlu_low': 'wlu - low',
                'wlu_moderate': 'wlu - moderate',
                'wlu_high': 'wlu - high',
                'ambiguity': 'ambiguity',
            }[rp_name]
            
            for t_idx in range(6):
                col_name = f"{rp_display}_t{t_idx}"
                
                # Find the result for this time index
                matching = [r for r in effect_results if r['time_idx'] == t_idx]
                if matching:
                    row[col_name] = matching[0][rp_name]
                else:
                    row[col_name] = 0.0
        
        output_rows.append(row)
    
    # Write CSV
    if output_rows:
        fieldnames = ['project_id', 'near_term_xrisk', 'effect_id', 'recipient_type']
        
        # Add all risk profile × time columns in the correct order
        for rp in ['neutral', 'upside', 'downside', 'combined', 'dmreu',
                   'wlu - low', 'wlu - moderate', 'wlu - high', 'ambiguity']:
            for t in range(6):
                fieldnames.append(f"{rp}_t{t}")
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
        
        if verbose:
            print(f"✓ Wrote {len(output_rows)} effect rows with {len(fieldnames)} columns")


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def process_gw_data(input_csv, output_csv, verbose=False):
    """Main processing pipeline.
    
    Args:
        input_csv: path to GiveWell percentiles CSV
        output_csv: path to write risk-adjusted output
        verbose: print progress information
    """
    if verbose:
        print("=" * 70)
        print("GIVEWELL COST-EFFECTIVENESS RISK ANALYSIS")
        print("=" * 70)
    
    # Parse input data
    data = parse_gw_csv(input_csv)
    
    # Process each effect type and time horizon
    results = []
    
    effect_types = [
        ('life_years_saved', 'life_years'),
        ('ylds_averted', 'ylds'),
        ('income_doublings', 'income_doublings'),
    ]
    
    for effect_key, recipient_type in effect_types:
        effect_data = data[effect_key]
        
        if verbose:
            print(f"\nProcessing {effect_key}...")
        
        for time_horizon in sorted(TIME_HORIZONS.keys(), key=lambda x: TIME_HORIZONS[x]):
            horizon_data = effect_data.get(time_horizon)
            
            if horizon_data is None:
                continue
            
            p5 = horizon_data['p5']
            mean = horizon_data['mean']
            p95 = horizon_data['p95']
            
            # Generate samples from percentiles
            draws = generate_samples_from_percentiles(p5, mean, p95)
            
            # Compute risk profiles
            risk_profiles = compute_all_risk_profiles(draws)
            
            # Store results
            result = {
                'effect_type': effect_key,
                'recipient_type': recipient_type,
                'time_horizon': time_horizon,
                'time_idx': TIME_HORIZONS[time_horizon],
                'input_p5': p5,
                'input_mean': mean,
                'input_p95': p95,
                **risk_profiles,
            }
            results.append(result)
    
    # Write output CSV
    write_output_csv(results, output_csv, verbose=verbose)
    
    if verbose:
        print(f"\n✓ Processing complete!")
        print(f"✓ Output written to: {output_csv}")
    
    return results


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="GiveWell Cost-Effectiveness Risk Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gw_risk_analysis.py input.csv output.csv
  python gw_risk_analysis.py input.csv output.csv --verbose
  
Risk Profiles:
  Informal: neutral, upside, downside, combined
  Formal:   dmreu, wlu (low/moderate/high), ambiguity
        """
    )
    
    parser.add_argument(
        'input_csv',
        type=str,
        help='Path to GiveWell percentiles CSV file'
    )
    
    parser.add_argument(
        'output_csv',
        type=str,
        help='Path for output risk-adjusted CSV file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print detailed progress information'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    input_path = Path(args.input_csv)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {args.input_csv}")
        sys.exit(1)
    
    # Run analysis
    try:
        process_gw_data(args.input_csv, args.output_csv, verbose=args.verbose)
    except Exception as e:
        print(f"ERROR: Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
