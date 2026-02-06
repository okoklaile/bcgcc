# ⚡ Quick Start: Fast Training Mode

## TL;DR - Two Commands

```bash
# 1. Preprocess data (one-time, ~8 minutes)
cd src
python3 prepare_data.py

# 2. Train (10-15 minutes for 100 epochs!)
python3 train.py
```

## Speed Comparison

| Before | After |
|--------|-------|
| 50 it/s | **500-800 it/s** |
| 7% GPU | **70-90% GPU** |
| 90s/epoch | **6-10s/epoch** |
| 2.5 hours | **10-15 minutes** |

## What Just Happened?

### Step 1: `prepare_data.py`
- Reads all 106 pickle files
- Processes 1.2M samples
- Saves 3 tensor files (~800MB)
- **Takes 8-10 minutes** (one time only!)

### Step 2: `train.py`
- Auto-detects preprocessed data
- Loads directly from tensors
- **10-15x faster training!**

## Expected Output

### During Preprocessing:
```
Processing train split...
Extracting 1,235,579 samples...
train data: 100%|████████████| 1235579/1235579

Tensor shapes:
  Features: torch.Size([1235579, 10, 14])
  Targets: torch.Size([1235579, 1])
  
File saved: 669.23 MB on disk
✓ Done!
```

### During Training:
```
⚡ Using FAST mode: preprocessed tensor loading
   Expected speed: 500-800 it/s

Epoch 1/100: 100%|██████| 4827/4827 [00:07<00:00, 623it/s]
                                              ^^^^^^^^^^
                                              Fast!
```

## FAQ

**Q: How much disk space needed?**
A: ~800MB for preprocessed tensors

**Q: How long does preprocessing take?**
A: 8-10 minutes

**Q: Can I skip preprocessing?**
A: Yes, training will work but be 10x slower

**Q: When to re-preprocess?**
A: Only if you change data or features, not for hyperparameters

## Full Documentation

See `FAST_TRAINING_GUIDE.md` for complete details.
