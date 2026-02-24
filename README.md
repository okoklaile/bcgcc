# BC-GCC: Behavior Cloning for Google Congestion Control

This repository contains the official implementation of the Behavior Cloning (BC) agent for Google Congestion Control (GCC) in WebRTC. The project aims to train a neural network policy to predict optimal bandwidth allocation based on expert trajectories from diverse network conditions.

## 🚀 Features

- **Robust Data Pipeline**: Handles diverse network traces (4G/5G, Wi-Fi, Wired) with varying delays and packet losses.
- **Advanced Feature Engineering**: Extracts 32-dimensional state vectors including delay gradients, trends, and queue delay estimates.
- **Stable Training**: Implements hard clipping, gradient scaling, and loss-weighted sampling to handle extreme network outliers.
- **Efficient Implementation**: optimized for GPU training with mixed precision (AMP) and pre-calculated tensor datasets.

## 📂 Project Structure

```
bc_gcc/
├── data/               # Dataset directory (see Data Preparation)
├── src/                # Source code
│   ├── config.py       # Configuration and hyperparameters
│   ├── dataset.py      # Data loading and processing
│   ├── model.py        # LSTM model architecture
│   ├── train.py        # Training loop and validation
│   └── prepare_data.py # Preprocessing script
├── tools/              # Analysis and visualization tools
├── checkpoints/        # Saved model checkpoints
├── logs/               # TensorBoard logs
└── requirements.txt    # Python dependencies
```

## 🛠️ Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/bc_gcc.git
    cd bc_gcc
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *Requires Python 3.8+ and PyTorch 2.0+.*

## 📊 Data Preparation

The training requires a dataset of network traces in `.pickle` format.

1.  **Place your data** in the `data/` directory, organized by subfolders (e.g., `data/ghent`, `data/norway`, `data/NY`, `data/opennetlab`).
2.  **Preprocess the data** for faster training (recommended):
    ```bash
    python src/prepare_data.py
    ```
    This script converts raw pickle files into optimized PyTorch tensors (`.pt`), providing a 10-15x speedup during training.

## 🏋️ Training

To start training the BC model:

```bash
python src/train.py
```

### Configuration
You can modify hyperparameters in `src/config.py`:
- `WINDOW_SIZE`: Length of the history window (default: 10 steps / 2 seconds).
- `BATCH_SIZE`: Training batch size (default: 2048).
- `LEARNING_RATE`: Initial learning rate (default: 2e-4).
- `LSTM_HIDDEN_SIZE`: Hidden dimension of the LSTM (default: 256).

### Monitoring
Monitor training progress using TensorBoard:
```bash
tensorboard --logdir logs
```

## 📈 Evaluation & Analysis

### 1. Statistical Analysis
Analyze the distribution of a specific trace:
```bash
python tools/analyze_gcc_data.py analyze data/ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle
```

### 2. Visualization
Generate plots for bandwidth, delay, and loss:
```bash
python tools/plot_gcc_data.py plot data/ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle reports/output.png
```

### 3. Coverage Analysis
Check the coverage of delay and loss scenarios across the entire dataset:
```bash
cd tools && python analyze_coverage.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
