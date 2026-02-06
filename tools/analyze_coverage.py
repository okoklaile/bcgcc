#!/usr/bin/env python3
"""
Analyze scenario coverage for all datasets
Focus on delay and loss ratio distribution
"""
import pickle
import numpy as np
from pathlib import Path
import sys

def analyze_dataset(directory):
    """Analyze a single dataset directory"""
    files = sorted(Path(directory).glob('*.pickle'))
    
    if not files:
        return None
    
    all_delays = []
    all_losses = []
    all_bandwidths = []
    
    file_stats = []
    
    for f in files:
        try:
            with open(f, 'rb') as fp:
                data = pickle.load(fp)
            
            if 'delay' not in data or len(data['delay']) == 0:
                continue
                
            delays = np.array(data['delay'])
            losses = np.array(data['loss_ratio']) if 'loss_ratio' in data else np.array([0])
            bandwidths = np.array(data['bandwidth_prediction']) if 'bandwidth_prediction' in data else np.array([0])
            
            # File-level stats
            file_stat = {
                'name': f.name,
                'delay_min': np.min(delays),
                'delay_max': np.max(delays),
                'delay_mean': np.mean(delays),
                'delay_std': np.std(delays),
                'loss_max': np.max(losses),
                'loss_mean': np.mean(losses),
                'loss_nonzero_pct': np.count_nonzero(losses) / len(losses) * 100,
                'samples': len(delays)
            }
            file_stats.append(file_stat)
            
            all_delays.extend(delays)
            all_losses.extend(losses)
            all_bandwidths.extend(bandwidths)
            
        except Exception as e:
            print(f"Error processing {f}: {e}")
            continue
    
    if not all_delays:
        return None
    
    all_delays = np.array(all_delays)
    all_losses = np.array(all_losses)
    all_bandwidths = np.array(all_bandwidths)
    
    # Calculate comprehensive statistics
    stats = {
        'dataset': directory,
        'num_files': len(files),
        'total_samples': len(all_delays),
        
        # Delay statistics
        'delay_min': np.min(all_delays),
        'delay_max': np.max(all_delays),
        'delay_mean': np.mean(all_delays),
        'delay_median': np.median(all_delays),
        'delay_std': np.std(all_delays),
        'delay_p95': np.percentile(all_delays, 95),
        'delay_p99': np.percentile(all_delays, 99),
        
        # Delay distribution
        'delay_low': np.sum(all_delays < 150) / len(all_delays) * 100,  # <150ms
        'delay_mid': np.sum((all_delays >= 150) & (all_delays < 300)) / len(all_delays) * 100,  # 150-300ms
        'delay_high': np.sum(all_delays >= 300) / len(all_delays) * 100,  # >300ms
        'delay_very_high': np.sum(all_delays >= 500) / len(all_delays) * 100,  # >500ms
        
        # Loss statistics
        'loss_min': np.min(all_losses),
        'loss_max': np.max(all_losses),
        'loss_mean': np.mean(all_losses),
        'loss_median': np.median(all_losses),
        
        # Loss distribution
        'loss_zero': np.sum(all_losses == 0) / len(all_losses) * 100,
        'loss_low': np.sum((all_losses > 0) & (all_losses <= 0.01)) / len(all_losses) * 100,  # 0-1%
        'loss_mid': np.sum((all_losses > 0.01) & (all_losses <= 0.05)) / len(all_losses) * 100,  # 1-5%
        'loss_high': np.sum(all_losses > 0.05) / len(all_losses) * 100,  # >5%
        'loss_very_high': np.sum(all_losses > 0.1) / len(all_losses) * 100,  # >10%
        
        # Bandwidth statistics
        'bw_min': np.min(all_bandwidths) / 1e6,
        'bw_max': np.max(all_bandwidths) / 1e6,
        'bw_mean': np.mean(all_bandwidths) / 1e6,
        
        'file_stats': file_stats
    }
    
    return stats

def print_dataset_summary(stats):
    """Print summary for a dataset"""
    print(f"\n{'='*80}")
    print(f"Dataset: {stats['dataset']}")
    print(f"{'='*80}")
    print(f"Files: {stats['num_files']}")
    print(f"Total samples: {stats['total_samples']:,}")
    
    print(f"\n--- DELAY ANALYSIS ---")
    print(f"Range: {stats['delay_min']:.1f} - {stats['delay_max']:.1f} ms")
    print(f"Mean: {stats['delay_mean']:.1f} ms (±{stats['delay_std']:.1f})")
    print(f"Median: {stats['delay_median']:.1f} ms")
    print(f"95th percentile: {stats['delay_p95']:.1f} ms")
    print(f"99th percentile: {stats['delay_p99']:.1f} ms")
    
    print(f"\nDelay Distribution:")
    print(f"  Low (<150ms):      {stats['delay_low']:6.2f}%  {'█' * int(stats['delay_low']/2)}")
    print(f"  Medium (150-300ms):{stats['delay_mid']:6.2f}%  {'█' * int(stats['delay_mid']/2)}")
    print(f"  High (>300ms):     {stats['delay_high']:6.2f}%  {'█' * int(stats['delay_high']/2)}")
    print(f"  Very High (>500ms):{stats['delay_very_high']:6.2f}%  {'█' * int(stats['delay_very_high']/2)}")
    
    print(f"\n--- LOSS RATIO ANALYSIS ---")
    print(f"Range: {stats['loss_min']*100:.4f}% - {stats['loss_max']*100:.2f}%")
    print(f"Mean: {stats['loss_mean']*100:.4f}%")
    print(f"Median: {stats['loss_median']*100:.4f}%")
    
    print(f"\nLoss Distribution:")
    print(f"  No loss (0%):      {stats['loss_zero']:6.2f}%  {'█' * int(stats['loss_zero']/2)}")
    print(f"  Low (0-1%):        {stats['loss_low']:6.2f}%  {'█' * int(stats['loss_low']/2) if stats['loss_low'] > 0.1 else '▏'}")
    print(f"  Medium (1-5%):     {stats['loss_mid']:6.2f}%  {'█' * int(stats['loss_mid']/2) if stats['loss_mid'] > 0.1 else '▏' if stats['loss_mid'] > 0 else ''}")
    print(f"  High (>5%):        {stats['loss_high']:6.2f}%  {'█' * int(stats['loss_high']/2) if stats['loss_high'] > 0.1 else '▏' if stats['loss_high'] > 0 else ''}")
    print(f"  Very High (>10%):  {stats['loss_very_high']:6.2f}%  {'█' * int(stats['loss_very_high']/2) if stats['loss_very_high'] > 0.1 else '▏' if stats['loss_very_high'] > 0 else ''}")
    
    print(f"\n--- BANDWIDTH ---")
    print(f"Range: {stats['bw_min']:.2f} - {stats['bw_max']:.2f} Mbps")
    print(f"Mean: {stats['bw_mean']:.2f} Mbps")

def print_top_files(stats, metric='loss'):
    """Print top files by metric"""
    file_stats = stats['file_stats']
    
    if metric == 'loss':
        sorted_files = sorted(file_stats, key=lambda x: x['loss_max'], reverse=True)[:5]
        print(f"\n--- TOP 5 FILES WITH HIGHEST LOSS ---")
        for i, f in enumerate(sorted_files, 1):
            print(f"{i}. {f['name']:<50} Max: {f['loss_max']*100:6.2f}%, Mean: {f['loss_mean']*100:6.4f}%, NonZero: {f['loss_nonzero_pct']:5.2f}%")
    
    elif metric == 'delay':
        sorted_files = sorted(file_stats, key=lambda x: x['delay_max'], reverse=True)[:5]
        print(f"\n--- TOP 5 FILES WITH HIGHEST DELAY ---")
        for i, f in enumerate(sorted_files, 1):
            print(f"{i}. {f['name']:<50} Max: {f['delay_max']:7.1f}ms, Mean: {f['delay_mean']:6.1f}ms, Std: {f['delay_std']:6.1f}ms")

def print_overall_coverage(all_stats):
    """Print overall coverage analysis"""
    print(f"\n\n{'='*80}")
    print(f"OVERALL COVERAGE ANALYSIS")
    print(f"{'='*80}\n")
    
    total_samples = sum(s['total_samples'] for s in all_stats)
    total_files = sum(s['num_files'] for s in all_stats)
    
    print(f"Total files: {total_files}")
    print(f"Total samples: {total_samples:,}\n")
    
    # Combined delay distribution
    print("--- DELAY COVERAGE ---")
    for s in all_stats:
        pct = s['total_samples'] / total_samples * 100
        print(f"{s['dataset']:<15} Low: {s['delay_low']:5.1f}%  Mid: {s['delay_mid']:5.1f}%  High: {s['delay_high']:5.1f}%  (Weight: {pct:5.1f}%)")
    
    # Combined loss distribution
    print("\n--- LOSS COVERAGE ---")
    for s in all_stats:
        pct = s['total_samples'] / total_samples * 100
        print(f"{s['dataset']:<15} Zero: {s['loss_zero']:5.1f}%  Low: {s['loss_low']:5.1f}%  Mid: {s['loss_mid']:5.1f}%  High: {s['loss_high']:5.1f}%")
    
    # Overall weighted averages
    total_delay_high = sum(s['total_samples'] * s['delay_high'] / 100 for s in all_stats) / total_samples
    total_loss_nonzero = sum(s['total_samples'] * (100 - s['loss_zero']) / 100 for s in all_stats) / total_samples
    
    print(f"\n--- OVERALL STATISTICS ---")
    print(f"High delay samples (>300ms): {total_delay_high:.2f}%")
    print(f"Non-zero loss samples: {total_loss_nonzero:.2f}%")
    
    # Coverage assessment
    print(f"\n--- COVERAGE ASSESSMENT ---")
    
    issues = []
    recommendations = []
    
    if total_delay_high < 5:
        issues.append(f"⚠️  High delay coverage LOW: {total_delay_high:.2f}% (recommend >10%)")
        recommendations.append("Consider adding more high-latency scenarios (e.g., ferry, long-distance)")
    else:
        print(f"✓ High delay coverage adequate: {total_delay_high:.2f}%")
    
    if total_loss_nonzero < 10:
        issues.append(f"⚠️  Loss scenarios SEVERELY LIMITED: {total_loss_nonzero:.2f}% (recommend >20%)")
        recommendations.append("CRITICAL: Need more packet loss scenarios for robust BC training")
    else:
        print(f"✓ Loss scenario coverage adequate: {total_loss_nonzero:.2f}%")
    
    if issues:
        print("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  • {rec}")

def main():
    # Check if running from tools/ or root directory
    if Path('data').exists():
        data_dir = 'data'
    elif Path('../data').exists():
        data_dir = '../data'
    else:
        print("Error: Cannot find data directory")
        return
    
    datasets = ['ghent', 'norway', 'NY', 'opennetlab']
    
    all_stats = []
    
    for dataset in datasets:
        dataset_path = Path(data_dir) / dataset
        if not dataset_path.exists():
            print(f"Warning: Directory {dataset_path} not found, skipping...")
            continue
        
        print(f"\nAnalyzing {dataset}...")
        stats = analyze_dataset(str(dataset_path))
        
        if stats:
            all_stats.append(stats)
            print_dataset_summary(stats)
            print_top_files(stats, 'loss')
            print_top_files(stats, 'delay')
    
    if all_stats:
        print_overall_coverage(all_stats)
    else:
        print("No data found!")

if __name__ == '__main__':
    main()
