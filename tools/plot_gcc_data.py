#!/usr/bin/env python3
"""
WebRTC GCC Data Visualization Tool
Requirements: pip install matplotlib
"""
import pickle
import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')  # 先设置backend
    import matplotlib.pyplot as plt  # 再导入pyplot
except ImportError:
    print("Error: matplotlib is required")
    print("Run: pip install matplotlib")
    sys.exit(1)

def load_pickle(file_path):
    """Load pickle file"""
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def plot_single_file(file_path, save_path=None):
    """Plot all metrics for a single file"""
    data = load_pickle(file_path)
    trace_name = data.get('trace_name', Path(file_path).stem)
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    fig.suptitle(f'WebRTC GCC Analysis: {trace_name}', fontsize=16, fontweight='bold')
    
    # Time axis (assuming each point represents 200ms)
    time_ms = [i * 200 for i in range(len(data.get('bandwidth_prediction', [])))]
    time_s = [t / 1000 for t in time_ms]  # Convert to seconds
    
    # Plot 1: Bandwidth and rates
    ax1 = axes[0]
    if 'bandwidth_prediction' in data:
        bw = [b / 1e6 for b in data['bandwidth_prediction']]  # Convert to Mbps
        ax1.plot(time_s, bw, label='Bandwidth Prediction', linewidth=2, alpha=0.8)
    if 'sending_rate' in data:
        send = [s / 1e6 for s in data['sending_rate']]
        ax1.plot(time_s, send, label='Sending Rate', linewidth=1.5, alpha=0.7)
    if 'receiving_rate' in data:
        recv = [r / 1e6 for r in data['receiving_rate']]
        ax1.plot(time_s, recv, label='Receiving Rate', linewidth=1, alpha=0.6, linestyle='--')
    
    ax1.set_ylabel('Rate (Mbps)', fontsize=12, fontweight='bold')
    ax1.set_title('Bandwidth Prediction vs Actual Rates', fontsize=13, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Delay
    ax2 = axes[1]
    if 'delay' in data:
        ax2.plot(time_s, data['delay'], color='orange', linewidth=1.5, alpha=0.8)
        ax2.axhline(y=sum(data['delay'])/len(data['delay']), 
                    color='r', linestyle='--', label=f'Average Delay', alpha=0.5)
    
    ax2.set_ylabel('Delay (ms)', fontsize=12, fontweight='bold')
    ax2.set_title('End-to-End Delay', fontsize=13, fontweight='bold')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Loss ratio
    ax3 = axes[2]
    if 'loss_ratio' in data:
        loss_percent = [l * 100 for l in data['loss_ratio']]
        ax3.plot(time_s, loss_percent, color='red', linewidth=1.5, alpha=0.8)
        ax3.fill_between(time_s, 0, loss_percent, color='red', alpha=0.2)
    
    ax3.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Loss Ratio (%)', fontsize=12, fontweight='bold')
    ax3.set_title('Packet Loss Ratio', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()

def plot_compare(file_paths, save_path=None):
    """Compare bandwidth predictions from multiple files"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = plt.cm.tab10(range(len(file_paths)))
    
    for i, fp in enumerate(file_paths):
        data = load_pickle(fp)
        trace_name = data.get('trace_name', Path(fp).stem)
        
        if 'bandwidth_prediction' in data:
            time_s = [i * 0.2 for i in range(len(data['bandwidth_prediction']))]
            bw = [b / 1e6 for b in data['bandwidth_prediction']]
            ax.plot(time_s, bw, label=trace_name, linewidth=2, 
                   alpha=0.7, color=colors[i])
    
    ax.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Bandwidth Prediction (Mbps)', fontsize=12, fontweight='bold')
    ax.set_title('Multi-Scenario Bandwidth Prediction Comparison', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison plot saved to: {save_path}")
    else:
        plt.show()

def plot_delay_distribution(file_paths, save_path=None):
    """Plot delay distribution histogram"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    all_delays = []
    labels = []
    
    for fp in file_paths:
        data = load_pickle(fp)
        if 'delay' in data:
            all_delays.append(data['delay'])
            labels.append(data.get('trace_name', Path(fp).stem))
    
    ax.hist(all_delays, bins=50, label=labels, alpha=0.6)
    ax.set_xlabel('Delay (ms)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title('Delay Distribution Histogram', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Delay distribution plot saved to: {save_path}")
    else:
        plt.show()

def main():
    if len(sys.argv) < 2:
        print("WebRTC GCC Data Visualization Tool")
        print("\nUsage:")
        print(f"  {sys.argv[0]} plot <file> [output.png]")
        print(f"  {sys.argv[0]} compare <file1> <file2> ... [output.png]")
        print(f"  {sys.argv[0]} delay-dist <file1> <file2> ... [output.png]")
        print("\nExamples:")
        print(f"  {sys.argv[0]} plot ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle")
        print(f"  {sys.argv[0]} plot ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle output.png")
        print(f"  {sys.argv[0]} compare ghent/*.pickle comparison.png")
        print(f"  {sys.argv[0]} delay-dist ghent/rates_delay_loss_gcc_report_*_0001.pickle")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'plot':
        if len(sys.argv) < 3:
            print("Error: file path required")
            sys.exit(1)
        save_path = sys.argv[3] if len(sys.argv) > 3 else None
        plot_single_file(sys.argv[2], save_path)
    
    elif command == 'compare':
        if len(sys.argv) < 3:
            print("Error: at least one file path required")
            sys.exit(1)
        
        # Check if last argument is save path
        if sys.argv[-1].endswith('.png'):
            file_paths = sys.argv[2:-1]
            save_path = sys.argv[-1]
        else:
            file_paths = sys.argv[2:]
            save_path = None
        
        plot_compare(file_paths, save_path)
    
    elif command == 'delay-dist':
        if len(sys.argv) < 3:
            print("Error: at least one file path required")
            sys.exit(1)
        
        # Check if last argument is save path
        if sys.argv[-1].endswith('.png'):
            file_paths = sys.argv[2:-1]
            save_path = sys.argv[-1]
        else:
            file_paths = sys.argv[2:]
            save_path = None
        
        plot_delay_distribution(file_paths, save_path)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
