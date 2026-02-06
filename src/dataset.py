"""
Dataset loader for BC-GCC training
"""
import pickle
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from typing import List, Dict, Tuple
import random

from config import Config


class GCCDataset(Dataset):
    """Dataset for GCC Behavior Cloning"""
    
    def __init__(self, pickle_files: List[str], config: Config, mode='train'):
        """
        Args:
            pickle_files: List of pickle file paths
            config: Configuration object
            mode: 'train', 'val', or 'test'
        """
        self.config = config
        self.mode = mode
        self.window_size = config.WINDOW_SIZE
        
        # Load and process all data
        self.samples = []
        self.weights = []
        
        print(f"\nLoading {mode} data...")
        for file_path in pickle_files:
            self._load_file(file_path)
        
        print(f"Total {mode} samples: {len(self.samples)}")
        if len(self.weights) > 0:
            print(f"Sample weight stats: min={min(self.weights):.2f}, "
                  f"max={max(self.weights):.2f}, "
                  f"mean={np.mean(self.weights):.2f}")
    
    def _load_file(self, file_path: str):
        """Load a single pickle file and extract samples"""
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            # Extract time series
            delays = np.array(data['delay'])
            losses = np.array(data['loss_ratio'])
            recv_rates = np.array(data['receiving_rate'])
            bw_preds = np.array(data['bandwidth_prediction'])
            
            # Check if this file should be oversampled
            oversample_mult = 1
            for oversample_file, mult in zip(self.config.OVERSAMPLE_FILES, 
                                             self.config.OVERSAMPLE_MULTIPLIERS):
                if oversample_file in file_path:
                    oversample_mult = mult
                    print(f"  Oversampling {Path(file_path).name} by {mult}x")
                    break
            
            # Create samples with sliding window
            for _ in range(oversample_mult):
                for t in range(self.window_size, len(delays)):
                    # Extract window
                    window_delays = delays[t-self.window_size:t]
                    window_losses = losses[t-self.window_size:t]
                    window_recv = recv_rates[t-self.window_size:t]
                    window_bw = bw_preds[t-self.window_size:t]
                    
                    # Compute features for each time step in window
                    features_sequence = []
                    
                    # Pre-compute window statistics (for efficiency)
                    prev_delay_grad = 0
                    
                    for i in range(self.window_size):
                        # === Basic features ===
                        delay = window_delays[i]
                        loss = window_losses[i]
                        recv_rate = window_recv[i]
                        prev_bw = window_bw[i-1] if i > 0 else window_bw[0]
                        
                        # === Delay gradient (1st order) ===
                        delay_grad = window_delays[i] - window_delays[i-1] if i > 0 else 0
                        
                        # === Effective throughput (considering loss) ===
                        throughput_effective = recv_rate * (1.0 - loss)
                        
                        # === Delay statistics (GCC core signals) ===
                        # Use data up to current time step
                        delay_window = window_delays[:i+1]
                        delay_mean = np.mean(delay_window)
                        delay_std = np.std(delay_window) if len(delay_window) > 1 else 0
                        delay_min = np.min(delay_window)
                        
                        # Queue delay (estimate of buffering delay)
                        queue_delay = delay - delay_min
                        
                        # Delay acceleration (2nd order gradient)
                        delay_accel = delay_grad - prev_delay_grad if i > 0 else 0
                        prev_delay_grad = delay_grad
                        
                        # Delay trend (linear regression slope on delay gradients)
                        # Simplified: use average of recent gradients as trend
                        if i >= 2:
                            recent_grads = [window_delays[j] - window_delays[j-1] 
                                          for j in range(1, i+1)]
                            # Simple trend: slope of linear fit
                            # Using numpy's polyfit would be more accurate but slower
                            # Approximation: difference between early and late averages
                            mid_point = len(recent_grads) // 2
                            early_avg = np.mean(recent_grads[:mid_point]) if mid_point > 0 else 0
                            late_avg = np.mean(recent_grads[mid_point:])
                            delay_trend = late_avg - early_avg
                        else:
                            delay_trend = 0
                        
                        # === Loss features ===
                        loss_change = loss - window_losses[i-1] if i > 0 else 0
                        
                        # === Bandwidth utilization ===
                        bw_utilization = recv_rate / (prev_bw + 1e-6)
                        
                        # === Receiving rate statistics ===
                        recv_window = window_recv[:i+1]
                        recv_rate_mean = np.mean(recv_window)
                        recv_rate_std = np.std(recv_window) if len(recv_window) > 1 else 0
                        
                        # === Assemble all features ===
                        core_feats = [
                            # Basic (6)
                            delay,
                            loss,
                            recv_rate,
                            prev_bw,
                            delay_grad,
                            throughput_effective,
                            
                            # Delay statistics (6)
                            delay_mean,
                            delay_std,
                            delay_min,
                            queue_delay,
                            delay_accel,
                            delay_trend,
                            
                            # Loss (1)
                            loss_change,
                            
                            # Bandwidth (3)
                            bw_utilization,
                            recv_rate_mean,
                            recv_rate_std,
                        ]
                        
                        # Reserved features (zeros for BC training)
                        reserved_feats = [0.0] * len(self.config.RESERVED_FEATURES)
                        
                        # Combine
                        features = core_feats + reserved_feats
                        features_sequence.append(features)
                    
                    features_sequence = np.array(features_sequence)  # [window_size, feature_dim]
                    
                    # Target (current bandwidth prediction)
                    target = bw_preds[t]
                    
                    # Compute sample weight based on loss and delay
                    current_loss = losses[t]
                    current_delay = delays[t]
                    
                    if current_loss > self.config.LOSS_THRESHOLD:
                        weight = self.config.LOSS_WEIGHT_HAS_LOSS
                    elif current_delay > self.config.HIGH_DELAY_THRESHOLD:
                        weight = self.config.LOSS_WEIGHT_HIGH_DELAY
                    else:
                        weight = self.config.LOSS_WEIGHT_NO_LOSS
                    
                    self.samples.append({
                        'features': features_sequence,
                        'target': target,
                        'loss_ratio': current_loss,
                        'delay': current_delay,
                    })
                    self.weights.append(weight)
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        weight = self.weights[idx]
        
        # Convert to tensors
        features = torch.FloatTensor(sample['features'])  # [window_size, feature_dim]
        target = torch.FloatTensor([sample['target']])
        weight = torch.FloatTensor([weight])
        
        return features, target, weight


def normalize_features(features: torch.Tensor, config: Config) -> torch.Tensor:
    """
    Normalize features to [0, 1] range with optional clipping
    
    Args:
        features: [batch, seq_len, feature_dim] or [seq_len, feature_dim]
        config: Config object with normalization stats
    
    Returns:
        Normalized features (clipped to [0, 1] if USE_CLIPPING is enabled)
    """
    normalized = features.clone()
    
    # Normalize each core feature
    for i, feat_name in enumerate(config.CORE_FEATURES):
        if feat_name in config.NORM_STATS:
            min_val = config.NORM_STATS[feat_name]['min']
            max_val = config.NORM_STATS[feat_name]['max']
            
            # Avoid division by zero
            range_val = max_val - min_val if max_val > min_val else 1.0
            
            # Clip extreme values if enabled (handles outliers like 455s delay)
            if hasattr(config, 'USE_CLIPPING') and config.USE_CLIPPING:
                if features.dim() == 3:  # [batch, seq, feat]
                    # Clamp values to [min_val, max_val] before normalization
                    clamped = torch.clamp(features[:, :, i], min_val, max_val)
                    normalized[:, :, i] = (clamped - min_val) / range_val
                else:  # [seq, feat]
                    clamped = torch.clamp(features[:, i], min_val, max_val)
                    normalized[:, i] = (clamped - min_val) / range_val
            else:
                # No clipping (original behavior)
                if features.dim() == 3:  # [batch, seq, feat]
                    normalized[:, :, i] = (features[:, :, i] - min_val) / range_val
                else:  # [seq, feat]
                    normalized[:, i] = (features[:, i] - min_val) / range_val
    
    # Reserved features are already 0, no need to normalize
    
    return normalized


def denormalize_target(target: torch.Tensor, config: Config) -> torch.Tensor:
    """Denormalize bandwidth prediction"""
    min_val = config.NORM_STATS['bandwidth_prediction']['min']
    max_val = config.NORM_STATS['bandwidth_prediction']['max']
    return target * (max_val - min_val) + min_val


def create_dataloaders(config: Config) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create train, validation, and test dataloaders
    
    Returns:
        train_loader, val_loader, test_loader
    """
    # Collect all pickle files
    all_files = []
    for dataset_name in config.DATASETS:
        dataset_path = Path(config.DATA_DIR) / dataset_name
        if dataset_path.exists():
            files = list(dataset_path.glob('*.pickle'))
            all_files.extend([str(f) for f in files])
    
    print(f"\nFound {len(all_files)} total files")
    
    # Shuffle and split
    random.seed(config.SEED)
    random.shuffle(all_files)
    
    n_total = len(all_files)
    n_train = int(n_total * config.TRAIN_RATIO)
    n_val = int(n_total * config.VAL_RATIO)
    
    train_files = all_files[:n_train]
    val_files = all_files[n_train:n_train + n_val]
    test_files = all_files[n_train + n_val:]
    
    print(f"Split: Train={len(train_files)}, Val={len(val_files)}, Test={len(test_files)}")
    
    # Create datasets
    train_dataset = GCCDataset(train_files, config, mode='train')
    val_dataset = GCCDataset(val_files, config, mode='val')
    test_dataset = GCCDataset(test_files, config, mode='test')
    
    # Create dataloaders (optimized for stability and speed)
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=True,
        num_workers=4,  # Reduced from 8 for better stability
        pin_memory=True if config.DEVICE == 'cuda' else False,
        # persistent_workers removed - can cause slowdowns in some systems
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=False,
        num_workers=4,  # Reduced from 8
        pin_memory=True if config.DEVICE == 'cuda' else False,
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=False,
        num_workers=4,  # Reduced from 8
        pin_memory=True if config.DEVICE == 'cuda' else False,
    )
    
    return train_loader, val_loader, test_loader


if __name__ == '__main__':
    # Test dataset loading
    config = Config()
    config.print_config()
    
    train_loader, val_loader, test_loader = create_dataloaders(config)
    
    # Test a batch
    for features, targets, weights in train_loader:
        print(f"\nBatch shapes:")
        print(f"  Features: {features.shape}")  # [batch, window_size, feature_dim]
        print(f"  Targets: {targets.shape}")
        print(f"  Weights: {weights.shape}")
        print(f"\nFeature stats:")
        print(f"  Min: {features.min():.2f}, Max: {features.max():.2f}")
        print(f"  Mean: {features.mean():.4f}, Std: {features.std():.4f}")
        print(f"\nTarget (bandwidth) stats:")
        print(f"  Min: {targets.min():.2f}, Max: {targets.max():.2f}")
        print(f"  Mean: {targets.mean():.2f}")
        break
