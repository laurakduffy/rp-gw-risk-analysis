#!/usr/bin/env python3
"""
Test script to verify GiveWell risk analysis setup.

This script tests:
1. All required modules can be imported
2. Risk analysis functions work correctly
3. Sample processing runs without errors
4. Output format is correct

Run: python test_setup.py
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import numpy as np
        print("  ✓ numpy")
    except ImportError as e:
        print(f"  ✗ numpy: {e}")
        return False
    
    try:
        import pandas as pd
        print("  ✓ pandas")
    except ImportError as e:
        print(f"  ✗ pandas: {e}")
        return False
    
    try:
        import scipy
        print("  ✓ scipy")
    except ImportError as e:
        print(f"  ✗ scipy: {e}")
        return False
    
    try:
        from risk_analysis import compute_dmreu, compute_wlu, compute_ambiguity_aversion
        print("  ✓ risk_analysis")
    except ImportError as e:
        print(f"  ✗ risk_analysis: {e}")
        print("  → Make sure risk_analysis.py is in the same directory")
        return False
    
    return True


def test_risk_functions():
    """Test that risk analysis functions work correctly."""
    print("\nTesting risk functions...")
    
    try:
        import numpy as np
        from risk_analysis import compute_dmreu, compute_wlu, compute_ambiguity_aversion
        
        # Create simple test distribution
        samples = np.linspace(1000, 5000, 1000)
        
        # Test each function
        neutral = np.mean(samples)
        dmreu = compute_dmreu(fit=None, p=0.05, samples=samples)
        wlu = compute_wlu(fit=None, c=0.05, samples=samples)
        ambiguity = compute_ambiguity_aversion(fit=None, k=4.0, samples=samples)
        
        print(f"  ✓ Risk-neutral EV: {neutral:.2f}")
        print(f"  ✓ DMREU: {dmreu:.2f}")
        print(f"  ✓ WLU: {wlu:.2f}")
        print(f"  ✓ Ambiguity: {ambiguity:.2f}")
        
        # Sanity check: risk-averse values should be less than or equal to neutral
        if dmreu <= neutral and wlu <= neutral:
            print("  ✓ Risk adjustments working correctly")
        else:
            print("  ⚠ Warning: Risk adjustments might not be working as expected")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sample_generation():
    """Test sample generation from percentiles."""
    print("\nTesting sample generation...")
    
    try:
        import numpy as np
        from gw_risk_analysis import generate_samples_from_percentiles
        
        # Test with typical GW data
        p5 = 10000
        mean = 14000
        p95 = 18000
        
        samples = generate_samples_from_percentiles(p5, mean, p95, n_samples=1000)
        
        # Check properties
        empirical_p5 = np.percentile(samples, 5)
        empirical_mean = np.mean(samples)
        empirical_p95 = np.percentile(samples, 95)
        
        print(f"  Input:  p5={p5:,}, mean={mean:,}, p95={p95:,}")
        print(f"  Output: p5={empirical_p5:,.0f}, mean={empirical_mean:,.0f}, p95={empirical_p95:,.0f}")
        
        # Sanity checks
        if 0.8 * p5 <= empirical_p5 <= 1.2 * p5:
            print("  ✓ 5th percentile preserved (±20%)")
        else:
            print("  ⚠ 5th percentile differs from input")
        
        if 0.8 * p95 <= empirical_p95 <= 1.2 * p95:
            print("  ✓ 95th percentile preserved (±20%)")
        else:
            print("  ⚠ 95th percentile differs from input")
        
        if len(samples) == 1000:
            print(f"  ✓ Generated {len(samples)} samples")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test the full analysis pipeline if example file exists."""
    print("\nTesting full pipeline...")
    
    example_file = Path("example_input.csv")
    if not example_file.exists():
        print("  ⊘ Example file not found (optional test)")
        return True
    
    try:
        from gw_risk_analysis import process_gw_data
        import os
        
        output_file = "test_output.csv"
        
        # Run analysis
        results = process_gw_data(str(example_file), output_file, verbose=False)
        
        print(f"  ✓ Processed {len(results)} effect×horizon combinations")
        
        # Check output file was created
        if Path(output_file).exists():
            print(f"  ✓ Output file created: {output_file}")
            
            # Check it has data
            import pandas as pd
            df = pd.read_csv(output_file)
            print(f"  ✓ Output has {len(df)} rows, {len(df.columns)} columns")
            
            # Clean up
            os.remove(output_file)
            print("  ✓ Cleaned up test file")
        else:
            print("  ✗ Output file not created")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("GIVEWELL RISK ANALYSIS - SETUP VERIFICATION")
    print("=" * 70)
    
    all_passed = True
    
    # Run tests
    if not test_imports():
        all_passed = False
        print("\n⚠ Fix import errors before continuing")
        print("   Run: pip install -r requirements.txt")
        sys.exit(1)
    
    if not test_risk_functions():
        all_passed = False
    
    if not test_sample_generation():
        all_passed = False
    
    if not test_full_pipeline():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print("\nYou're ready to run the analysis!")
        print("\nNext step:")
        print("  python gw_risk_analysis.py input.csv output.csv --verbose")
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 70)
        print("\nPlease fix the errors above before running the analysis.")
        sys.exit(1)


if __name__ == "__main__":
    main()
