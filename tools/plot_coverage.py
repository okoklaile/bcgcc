#!/usr/bin/env python3
"""
Visualize dataset coverage
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plot_coverage_summary():
    """Create comprehensive coverage visualization"""
    
    fig = plt.figure(figsize=(16, 12))
    
    # Dataset information
    datasets = ['ghent', 'norway', 'NY', 'opennetlab']
    samples = [90202, 322515, 481200, 3992]
    files = [40, 59, 25, 9]
    
    # Delay distribution (%)
    delay_low = [89.87, 37.61, 35.65, 68.06]
    delay_mid = [5.29, 15.46, 22.75, 17.36]
    delay_high = [4.85, 46.93, 41.60, 14.58]
    
    # Loss distribution (%)
    loss_zero = [99.49, 99.61, 98.85, 98.22]
    loss_nonzero = [0.51, 0.39, 1.15, 1.78]
    
    # Bandwidth (Mbps)
    bandwidth_mean = [1.74, 0.09, 3.36, 0.65]
    
    # Create subplots
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Dataset sizes
    ax1 = fig.add_subplot(gs[0, 0])
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    bars = ax1.bar(datasets, samples, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('Number of Samples', fontsize=11, fontweight='bold')
    ax1.set_title('Dataset Sizes', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, max(samples) * 1.1)
    for i, (bar, s) in enumerate(zip(bars, samples)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{s:,}\n({s/sum(samples)*100:.1f}%)',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Delay distribution stacked bar
    ax2 = fig.add_subplot(gs[0, 1])
    x = np.arange(len(datasets))
    width = 0.6
    
    p1 = ax2.bar(x, delay_low, width, label='Low (<150ms)', color='#2ecc71', alpha=0.8)
    p2 = ax2.bar(x, delay_mid, width, bottom=delay_low, label='Medium (150-300ms)', color='#f39c12', alpha=0.8)
    p3 = ax2.bar(x, delay_high, width, bottom=np.array(delay_low)+np.array(delay_mid), 
                 label='High (>300ms)', color='#e74c3c', alpha=0.8)
    
    ax2.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Delay Distribution by Dataset', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(datasets)
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_ylim(0, 105)
    
    # Add percentages on bars
    for i, (d1, d2, d3) in enumerate(zip(delay_low, delay_mid, delay_high)):
        if d3 > 3:
            ax2.text(i, d1 + d2 + d3/2, f'{d3:.1f}%', ha='center', va='center', 
                    fontsize=9, fontweight='bold', color='white')
    
    # 3. Loss distribution
    ax3 = fig.add_subplot(gs[0, 2])
    x = np.arange(len(datasets))
    width = 0.6
    
    p1 = ax3.bar(x, loss_zero, width, label='No Loss (0%)', color='#95a5a6', alpha=0.7)
    p2 = ax3.bar(x, loss_nonzero, width, bottom=loss_zero, label='Has Loss (>0%)', 
                 color='#e74c3c', alpha=0.9, edgecolor='darkred', linewidth=2)
    
    ax3.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold')
    ax3.set_title('Packet Loss Distribution', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(datasets)
    ax3.legend(loc='lower left', fontsize=9)
    ax3.grid(axis='y', alpha=0.3)
    ax3.set_ylim(0, 105)
    
    # Highlight loss percentage
    for i, loss in enumerate(loss_nonzero):
        ax3.text(i, 101, f'{loss:.2f}%', ha='center', va='bottom', 
                fontsize=10, fontweight='bold', color='red')
    
    # 4. Bandwidth comparison
    ax4 = fig.add_subplot(gs[1, 0])
    bars = ax4.barh(datasets, bandwidth_mean, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax4.set_xlabel('Mean Bandwidth (Mbps)', fontsize=11, fontweight='bold')
    ax4.set_title('Average Bandwidth by Dataset', fontsize=12, fontweight='bold')
    ax4.grid(axis='x', alpha=0.3)
    for i, (bar, bw) in enumerate(zip(bars, bandwidth_mean)):
        width = bar.get_width()
        ax4.text(width, bar.get_y() + bar.get_height()/2.,
                f'{bw:.2f}',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    # 5. Coverage heatmap
    ax5 = fig.add_subplot(gs[1, 1:])
    
    # Create coverage matrix
    coverage_data = np.array([
        [89.87, 5.29, 4.85, 0.51],   # ghent
        [37.61, 15.46, 46.93, 0.39],  # norway
        [35.65, 22.75, 41.60, 1.15],  # NY
        [68.06, 17.36, 14.58, 1.78],  # opennetlab
    ])
    
    im = ax5.imshow(coverage_data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    
    ax5.set_xticks(np.arange(4))
    ax5.set_yticks(np.arange(4))
    ax5.set_xticklabels(['Low Delay\n(<150ms)', 'Mid Delay\n(150-300ms)', 
                         'High Delay\n(>300ms)', 'Has Loss\n(>0%)'], fontsize=10)
    ax5.set_yticklabels(datasets, fontsize=11, fontweight='bold')
    
    # Add text annotations
    for i in range(4):
        for j in range(4):
            text = ax5.text(j, i, f'{coverage_data[i, j]:.1f}%',
                          ha="center", va="center", color="black", fontsize=11, fontweight='bold')
    
    ax5.set_title('Coverage Heatmap (% of samples in each category)', fontsize=12, fontweight='bold')
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax5, orientation='vertical', pad=0.02)
    cbar.set_label('Percentage (%)', fontsize=10, fontweight='bold')
    
    # 6. Summary statistics
    ax6 = fig.add_subplot(gs[2, :])
    ax6.axis('off')
    
    summary_text = f"""
    COVERAGE SUMMARY
    
    ✓ STRENGTHS:
      • Total samples: {sum(samples):,} across {sum(files)} files
      • Excellent high-delay coverage in norway (46.93%) and NY (41.60%)
      • Diverse scenarios: urban subway, rural ferry, bicycle, bus, car
      • Good bandwidth range: 0.09 - 3.36 Mbps average
    
    ✗ CRITICAL GAPS:
      • Packet loss severely limited: Only 0.51-1.78% of samples have any loss
      • Overall <1% of samples have packet loss (weighted average)
      • Risk: BC model won't learn proper congestion response
    
    ⚠ RECOMMENDATIONS:
      1. Oversample packet loss scenarios 20-50x during training
      2. Use weighted loss function (50x weight for loss>0 samples)
      3. Consider data augmentation to add synthetic packet loss
      4. Focus evaluation on extreme scenarios (high delay + loss)
      5. Use NY dataset (best loss coverage) for validation
    """
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
            fontsize=11, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.suptitle('WebRTC GCC Dataset Coverage Analysis', 
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.savefig('coverage_analysis.png', dpi=300, bbox_inches='tight')
    print("Coverage visualization saved to: coverage_analysis.png")
    
    # Create second figure for detailed loss analysis
    fig2, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig2.suptitle('Detailed Packet Loss Analysis', fontsize=16, fontweight='bold')
    
    # Top files with loss
    top_files = [
        ('4G_3mbps', 20.33, 96.00, 'opennetlab'),
        ('bus57New', 1.21, 99.82, 'NY'),
        ('Ferry4', 1.57, 99.76, 'NY'),
        ('7trainNew', 1.43, 99.72, 'NY'),
        ('bus62New', 0.23, 99.84, 'NY'),
    ]
    
    ax = axes[0, 0]
    files_names = [f[0] for f in top_files]
    nonzero_pct = [f[1] for f in top_files]
    colors_map = {'opennetlab': '#f39c12', 'NY': '#e74c3c'}
    colors_bars = [colors_map[f[3]] for f in top_files]
    
    bars = ax.barh(files_names, nonzero_pct, color=colors_bars, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_xlabel('% of Samples with Loss > 0', fontsize=11, fontweight='bold')
    ax.set_title('Top 5 Files by Loss Coverage', fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    for bar, pct in zip(bars, nonzero_pct):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
               f' {pct:.2f}%', va='center', fontsize=10, fontweight='bold')
    
    # Max loss values
    ax = axes[0, 1]
    max_loss = [f[2] for f in top_files]
    bars = ax.barh(files_names, max_loss, color=colors_bars, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_xlabel('Maximum Loss Ratio (%)', fontsize=11, fontweight='bold')
    ax.set_title('Maximum Loss Events', fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    for bar, loss in zip(bars, max_loss):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
               f' {loss:.1f}%', va='center', fontsize=10, fontweight='bold')
    
    # Loss distribution across datasets
    ax = axes[1, 0]
    loss_categories = ['0%', '0-1%', '1-5%', '>5%']
    ghent_loss = [99.49, 0.00, 0.03, 0.48]
    norway_loss = [99.61, 0.00, 0.00, 0.39]
    ny_loss = [98.85, 0.01, 0.10, 1.04]
    opennet_loss = [98.22, 0.00, 0.05, 1.73]
    
    x = np.arange(len(loss_categories))
    width = 0.2
    
    ax.bar(x - 1.5*width, ghent_loss, width, label='ghent', alpha=0.7)
    ax.bar(x - 0.5*width, norway_loss, width, label='norway', alpha=0.7)
    ax.bar(x + 0.5*width, ny_loss, width, label='NY', alpha=0.7)
    ax.bar(x + 1.5*width, opennet_loss, width, label='opennetlab', alpha=0.7)
    
    ax.set_ylabel('Percentage of Samples (%)', fontsize=11, fontweight='bold')
    ax.set_xlabel('Loss Ratio Range', fontsize=11, fontweight='bold')
    ax.set_title('Loss Distribution Breakdown', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(loss_categories)
    ax.legend(fontsize=9)
    ax.set_yscale('log')
    ax.grid(axis='y', alpha=0.3)
    
    # Recommendation text
    ax = axes[1, 1]
    ax.axis('off')
    
    rec_text = """
    KEY FINDINGS:
    
    1. 4G_3mbps.pickle is the BEST file:
       • 20.33% samples have loss
       • Should be oversampled 50x
    
    2. NY dataset is most valuable:
       • 4 out of 5 top files
       • Best for validation/test
    
    3. Training Strategy:
       ┌─────────────────────────────┐
       │ Sample Weight Recommendation │
       ├─────────────────────────────┤
       │ No loss:      1x             │
       │ Loss 0-1%:    10x            │
       │ Loss 1-5%:    30x            │
       │ Loss >5%:     50x            │
       └─────────────────────────────┘
    
    4. Data Augmentation Ideas:
       • Add synthetic loss to traces
       • Simulate network handoffs
       • Create "worst case" scenarios
    
    5. Model Evaluation:
       • MUST test on high-loss traces
       • Separate metrics for loss>0
       • Compare to GCC on edge cases
    """
    
    ax.text(0.05, 0.95, rec_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', family='monospace',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('loss_analysis.png', dpi=300, bbox_inches='tight')
    print("Loss analysis saved to: loss_analysis.png")

if __name__ == '__main__':
    plot_coverage_summary()
