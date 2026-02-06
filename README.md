# BC-GCC Project

Behavior Cloning for Google Congestion Control (GCC) Algorithm

## Project Structure

```
bc_gcc/
├── data/               # Raw datasets (133 pickle files, 898K samples)
│   ├── ghent/         # 40 files - bicycle, bus, car, train scenarios
│   ├── norway/        # 59 files - bus, ferry scenarios  
│   ├── NY/            # 25 files - subway, bus scenarios
│   └── opennetlab/    # 9 files - 4G/5G controlled tests
│
├── tools/             # Analysis and visualization tools
│   ├── view_pickle.py         # View pickle file contents
│   ├── analyze_gcc_data.py    # Statistical analysis
│   ├── plot_gcc_data.py       # Visualization (requires matplotlib)
│   ├── analyze_coverage.py    # Dataset coverage analysis
│   └── plot_coverage.py       # Coverage visualization
│
├── docs/              # Documentation
│   ├── README.md              # Detailed usage guide
│   ├── QUICK_REFERENCE.md     # Quick reference
│   ├── COVERAGE_REPORT.md     # Coverage analysis report
│   └── ANALYSIS_SUMMARY.md    # Analysis summary (中文)
│
├── reports/           # Generated analysis reports and plots
│   ├── coverage_analysis.png
│   ├── loss_analysis.png
│   └── bicycle_plot.png
│
├── outputs/           # Exported data (CSV, etc.)
│   └── bicycle_0001.csv
│
├── quick_start.sh     # Quick start script
└── view_analysis.sh   # View analysis results
```

## Quick Start

```bash
# 1. Run quick start script
./quick_start.sh

# 2. Analyze a dataset
python3 tools/analyze_gcc_data.py analyze data/ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle

# 3. Generate visualization
python3 tools/plot_gcc_data.py plot data/ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle reports/output.png

# 4. Run coverage analysis
cd tools && python3 analyze_coverage.py && cd ..

# 5. View analysis results
./view_analysis.sh
```

## Dataset Overview

- **Total samples:** 897,909 data points
- **Total files:** 133 pickle files
- **High delay coverage:** Good (46.93% in norway, 41.60% in NY)
- **Packet loss coverage:** ⚠️ Limited (<1% samples have loss)

## Key Findings

✅ **Strengths:**
- Excellent high-delay scenarios
- Large and diverse dataset
- Real-world mobility scenarios

❌ **Critical Gap:**
- Packet loss scenarios severely limited
- Requires oversampling for BC training

## Training BC Model

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start training
cd src
python train.py

# 3. Monitor training
tensorboard --logdir ../logs
```

### Model Architecture

- **Input**: [batch, window_size=10, features=14]
  - 6 core features (delay, loss, rate, etc.)
  - 8 reserved features (for future RL)
- **LSTM**: 2 layers × 128 hidden units
- **Output**: Bandwidth prediction (bps)
- **Parameters**: ~155K

### Key Features

✅ **Data Resampling**: Oversample packet loss scenarios 20-50x
✅ **Sample Weighting**: 50x weight for loss>0 samples  
✅ **Reserved Inputs**: 8 slots for future RL features
✅ **Gradient Clipping**: Prevent LSTM gradient explosion
✅ **Early Stopping**: Patience=10 epochs

For detailed training guide, see `README_TRAINING.md`

## Next Steps

1. Review analysis reports in `docs/`
2. Check visualization in `reports/`
3. Start BC training: `cd src && python train.py`
4. Monitor with Tensorboard
5. Evaluate on test set
6. Fine-tune with RL (future work)

For detailed information, see `docs/ANALYSIS_SUMMARY.md` (中文) or `docs/COVERAGE_REPORT.md` (English).
