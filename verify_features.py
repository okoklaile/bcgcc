#!/usr/bin/env python3
"""
Verify that the enhanced features are correctly implemented
"""
import sys
sys.path.insert(0, 'src')

from config import Config
import numpy as np

def main():
    config = Config()
    
    print("="*80)
    print("Feature Enhancement Verification")
    print("="*80)
    
    # Check feature count
    print(f"\n✓ Checking feature configuration...")
    print(f"  Core features: {len(config.CORE_FEATURES)}")
    print(f"  Reserved features: {len(config.RESERVED_FEATURES)}")
    print(f"  Total dimension: {config.TOTAL_FEATURE_DIM}")
    
    expected_core = 16
    expected_total = 24
    
    if len(config.CORE_FEATURES) == expected_core:
        print(f"  ✓ Core features count correct: {expected_core}")
    else:
        print(f"  ✗ ERROR: Expected {expected_core} core features, got {len(config.CORE_FEATURES)}")
        return False
    
    if config.TOTAL_FEATURE_DIM == expected_total:
        print(f"  ✓ Total dimension correct: {expected_total}")
    else:
        print(f"  ✗ ERROR: Expected {expected_total} total dim, got {config.TOTAL_FEATURE_DIM}")
        return False
    
    # Check feature names
    print(f"\n✓ Core features:")
    for i, feat in enumerate(config.CORE_FEATURES):
        print(f"  {i+1:2d}. {feat}")
    
    # Check normalization stats
    print(f"\n✓ Checking normalization stats...")
    required_features = config.CORE_FEATURES + ['bandwidth_prediction']
    
    missing = []
    for feat in required_features:
        if feat not in config.NORM_STATS:
            missing.append(feat)
    
    if not missing:
        print(f"  ✓ All features have normalization stats")
    else:
        print(f"  ✗ ERROR: Missing normalization stats for: {missing}")
        return False
    
    # Check new features
    new_features = [
        'throughput_effective',
        'delay_mean', 'delay_std', 'delay_min', 'queue_delay',
        'delay_accel', 'delay_trend',
        'loss_change',
        'bw_utilization', 'recv_rate_mean', 'recv_rate_std'
    ]
    
    print(f"\n✓ New features added ({len(new_features)}):")
    for feat in new_features:
        if feat in config.CORE_FEATURES:
            print(f"  ✓ {feat}")
        else:
            print(f"  ✗ {feat} NOT FOUND")
            return False
    
    print(f"\n{'='*80}")
    print("✓ All verification checks passed!")
    print("='*80")
    print("\nNext steps:")
    print("  1. Delete old preprocessed data:")
    print("     rm data/processed/*.pt")
    print("\n  2. Run preprocessing:")
    print("     cd src && python3 prepare_data.py")
    print("\n  3. Train model:")
    print("     python3 train.py")
    print("='*80")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
