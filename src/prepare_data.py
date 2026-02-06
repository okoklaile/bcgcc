"""
Data Preprocessing Script for BC-GCC

This script preprocesses all pickle files into PyTorch tensor files for faster training.
Run this once before training to achieve 10-15x speedup.

Usage:
    python3 prepare_data.py
"""
import torch
from torch.utils.data import TensorDataset
from pathlib import Path
import time
from tqdm import tqdm

from config import Config
from dataset import create_dataloaders


def prepare_split(dataloader, split_name: str, save_path: Path):
    """
    Prepare data for one split (train/val/test)
    
    Args:
        dataloader: PyTorch DataLoader
        split_name: 'train', 'val', or 'test'
        save_path: Path to save the processed tensors
    """
    print(f"\n{'='*80}")
    print(f"Processing {split_name} split...")
    print(f"{'='*80}")
    
    # Extract all data from dataset
    features_list = []
    targets_list = []
    weights_list = []
    
    dataset = dataloader.dataset
    total_samples = len(dataset)
    
    print(f"Extracting {total_samples:,} samples...")
    for i in tqdm(range(total_samples), desc=f'{split_name} data'):
        features, targets, weights = dataset[i]
        features_list.append(features)
        targets_list.append(targets)
        weights_list.append(weights)
    
    # Stack into large tensors
    print(f"Stacking tensors...")
    features_tensor = torch.stack(features_list)  # [N, window_size, feature_dim]
    targets_tensor = torch.stack(targets_list)    # [N, 1]
    weights_tensor = torch.stack(weights_list)    # [N, 1]
    
    # Create data dictionary
    data_dict = {
        'features': features_tensor,
        'targets': targets_tensor,
        'weights': weights_tensor,
        'num_samples': total_samples,
    }
    
    # Print statistics
    print(f"\nTensor shapes:")
    print(f"  Features: {features_tensor.shape}")
    print(f"  Targets: {targets_tensor.shape}")
    print(f"  Weights: {weights_tensor.shape}")
    print(f"\nMemory usage:")
    features_mb = features_tensor.numel() * 4 / (1024**2)  # 4 bytes per float32
    targets_mb = targets_tensor.numel() * 4 / (1024**2)
    weights_mb = weights_tensor.numel() * 4 / (1024**2)
    total_mb = features_mb + targets_mb + weights_mb
    print(f"  Features: {features_mb:.2f} MB")
    print(f"  Targets: {targets_mb:.2f} MB")
    print(f"  Weights: {weights_mb:.2f} MB")
    print(f"  Total: {total_mb:.2f} MB")
    
    # Save to disk
    print(f"\nSaving to {save_path}...")
    torch.save(data_dict, save_path)
    
    # Verify file size
    file_size_mb = save_path.stat().st_size / (1024**2)
    print(f"File saved: {file_size_mb:.2f} MB on disk")
    
    return data_dict


def main():
    """Main preprocessing function"""
    print("="*80)
    print("BC-GCC Data Preprocessing")
    print("="*80)
    print("\nThis will preprocess all data into tensor files for faster training.")
    print("This needs to be run only once.\n")
    
    # Load config
    config = Config()
    
    # Create output directory
    processed_dir = Path(config.DATA_DIR) / 'processed'
    processed_dir.mkdir(exist_ok=True, parents=True)
    print(f"Output directory: {processed_dir}")
    
    # Start timer
    start_time = time.time()
    
    # Create original dataloaders (this will process all data)
    print("\n" + "="*80)
    print("Step 1: Loading and processing original data...")
    print("="*80)
    train_loader, val_loader, test_loader = create_dataloaders(config)
    
    # Prepare each split
    print("\n" + "="*80)
    print("Step 2: Converting to tensor format...")
    print("="*80)
    
    train_path = processed_dir / 'train_tensors.pt'
    val_path = processed_dir / 'val_tensors.pt'
    test_path = processed_dir / 'test_tensors.pt'
    
    train_data = prepare_split(train_loader, 'train', train_path)
    val_data = prepare_split(val_loader, 'val', val_path)
    test_data = prepare_split(test_loader, 'test', test_path)
    
    # Calculate total time
    elapsed_time = time.time() - start_time
    
    # Print summary
    print("\n" + "="*80)
    print("Preprocessing Complete!")
    print("="*80)
    print(f"\nTotal time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print(f"\nProcessed files:")
    print(f"  Train: {train_path}")
    print(f"  Val:   {val_path}")
    print(f"  Test:  {test_path}")
    
    total_size = (train_path.stat().st_size + 
                  val_path.stat().st_size + 
                  test_path.stat().st_size) / (1024**2)
    print(f"\nTotal disk usage: {total_size:.2f} MB")
    
    print("\n" + "="*80)
    print("Next Steps:")
    print("="*80)
    print("1. Run training with preprocessed data:")
    print("   python3 train.py")
    print("\n2. Training will automatically detect and use the preprocessed files")
    print("\n3. Expected speedup: 10-15x faster (500-800 it/s)")
    print("="*80)


if __name__ == '__main__':
    main()
