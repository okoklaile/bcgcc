# WebRTC GCC Dataset Coverage Analysis Report

Generated: 2026-01-24

## 📊 Executive Summary

**Total Dataset:**
- **Files:** 133 pickle files
- **Samples:** 897,909 data points
- **Datasets:** ghent (40 files), norway (59 files), NY (25 files), opennetlab (9 files)

---

## 🚨 CRITICAL FINDINGS

### ❌ **SEVERE ISSUE: Packet Loss Coverage**
- **Only 0.01% of samples have non-zero loss**
- 99%+ of all samples are zero-loss scenarios
- **This is INSUFFICIENT for BC training**

### ⚠️ **WARNING: High Delay Coverage** 
- Overall high delay (>300ms): 0.40% (weighted average)
- However, norway and NY datasets individually have good coverage
- Issue is weighting - ghent is oversampled in proportion

---

## 📈 Detailed Analysis by Dataset

### 1. **Ghent Dataset** (40 files, 90,202 samples)
```
Delay Distribution:
  Low (<150ms):     89.87%  ████████████████████████████████████████████
  Medium (150-300): 5.29%   ██
  High (>300ms):    4.85%   ██

Loss Distribution:
  No loss:          99.49%  █████████████████████████████████████████████
  Has loss:         0.51%   ▏
```

**Characteristics:**
- ✅ Good for learning normal network behavior
- ✅ Stable low-latency scenarios (bicycle, car, bus)
- ❌ Very limited packet loss
- ❌ Limited high-delay scenarios

**Best for:** Learning bandwidth increase strategies in good network conditions

---

### 2. **Norway Dataset** (59 files, 322,515 samples - 35.9% of total)
```
Delay Distribution:
  Low (<150ms):     37.61%  ██████████████████
  Medium (150-300): 15.46%  ███████
  High (>300ms):    46.93%  ███████████████████████  ← EXCELLENT!

Loss Distribution:
  No loss:          99.61%  █████████████████████████████████████████████
  Has loss:         0.39%   ▏
```

**Characteristics:**
- ✅✅ **EXCELLENT high-delay coverage** (46.93% >300ms)
- ✅ Includes ferry and train scenarios with network handoffs
- ✅ Extreme delays up to 231 seconds (network disconnections)
- ❌ Still very limited packet loss

**Best for:** Learning congestion response and delay tolerance

---

### 3. **NY Dataset** (25 files, 481,200 samples - 53.6% of total!)
```
Delay Distribution:
  Low (<150ms):     35.65%  █████████████████
  Medium (150-300): 22.75%  ███████████
  High (>300ms):    41.60%  ████████████████████  ← EXCELLENT!

Loss Distribution:
  No loss:          98.85%  █████████████████████████████████████████████
  Has loss:         1.15%   ▏  ← BEST among all datasets
```

**Characteristics:**
- ✅✅ **BEST overall coverage**
- ✅✅ Best packet loss coverage (1.15% non-zero)
- ✅ Excellent delay distribution
- ✅ Urban mobility scenarios (subway, bus)
- ✅ Includes extreme cases (delays up to 455 seconds)

**Best for:** Most realistic training scenarios with both delay and loss

---

### 4. **OpenNetLab Dataset** (9 files, 3,992 samples - only 0.4%)
```
Delay Distribution:
  Low (<150ms):     68.06%  ██████████████████████████████████
  Medium (150-300): 17.36%  ████████
  High (>300ms):    14.58%  ███████

Loss Distribution:
  No loss:          98.22%  █████████████████████████████████████████████
  Has loss:         1.78%   ▏  ← Second best
```

**Characteristics:**
- ✅ Controlled 4G/5G/Wired scenarios
- ✅ Good for specific bandwidth scenarios
- ⚠️ Very small dataset (only 0.4% of total)
- ℹ️ One file (4G_3mbps) has 20.33% non-zero loss samples

**Best for:** Testing specific network types, but too small to matter

---

## 🎯 Coverage Assessment

### What You Have ✅

| Scenario | Coverage | Quality | Notes |
|----------|----------|---------|-------|
| Low latency (<150ms) | Excellent | ★★★★★ | 89.9% in ghent |
| High latency (>300ms) | **Good** | ★★★★☆ | 46.9% in norway, 41.6% in NY |
| Extreme latency (>1s) | **Good** | ★★★★☆ | Network handoffs well represented |
| Various bandwidth | Good | ★★★★☆ | 0.09 - 3.36 Mbps mean across datasets |

### What You're Missing ❌

| Scenario | Coverage | Quality | Impact on BC Training |
|----------|----------|---------|----------------------|
| Moderate packet loss (1-5%) | **Terrible** | ★☆☆☆☆ | **CRITICAL PROBLEM** |
| High packet loss (>5%) | **Terrible** | ★☆☆☆☆ | **CRITICAL PROBLEM** |
| Sustained congestion | Poor | ★★☆☆☆ | Model won't learn proper backoff |
| Loss + High delay combo | Very poor | ★☆☆☆☆ | Won't handle worst-case scenarios |

---

## 🔍 Top Files to Focus On

### Files with Most Packet Loss:
1. **4G_3mbps.pickle** (opennetlab) - 20.33% samples with loss, max 96%
2. **BusBrooklyn_bus57New.pickle** (NY) - 1.21% samples with loss, max 99.82%
3. **Ferry4.pickle** (NY) - 1.57% samples with loss, max 99.76%
4. **7trainNew.pickle** (NY) - 1.43% samples with loss, max 99.72%

### Files with Extreme Delays:
1. **7BtrainNew.pickle** (NY) - Max 454,963ms, mean 264,545ms
2. **7trainNew.pickle** (NY) - Max 235,418ms, mean 118,446ms
3. **train_2011-02-11_1530CET.pickle** (norway) - Max 231,575ms

---

## 💡 Recommendations for BC Training

### CRITICAL: Address Packet Loss Gap

#### Option 1: Oversample Loss Scenarios (Recommended)
```python
# During dataset construction
loss_files = [
    'opennetlab/rates_delay_loss_gcc_4G_3mbps.pickle',
    'NY/rates_delay_loss_gcc_BusBrooklyn_bus57New.pickle',
    'NY/rates_delay_loss_gcc_Ferry_Ferry4.pickle',
    'NY/rates_delay_loss_gcc_7Train_7trainNew.pickle'
]

# Sample these files 20-50x more frequently
# Or extract only samples with loss > 0 and repeat
```

#### Option 2: Data Augmentation
```python
# Add synthetic packet loss to existing traces
def augment_with_loss(data, loss_prob=0.05):
    # Randomly add packet loss events
    # Simulate GCC's reaction
    pass
```

#### Option 3: Weighted Loss Function
```python
# During training, weight samples by rarity
loss_weight = 1.0 if loss_ratio == 0 else 50.0
```

### Dataset Weighting Strategy

Current problem: **NY dataset dominates (53.6%)** but ghent is least useful (10%)

**Recommended Weighting:**
```python
dataset_weights = {
    'NY': 0.40,          # Best overall coverage
    'norway': 0.35,      # Excellent high delay
    'opennetlab': 0.15,  # Small but has loss scenarios
    'ghent': 0.10        # Limited value, good for baseline
}
```

### Training Strategy

```python
# Phase 1: Learn basic behavior (Epochs 1-30)
# Use all data, focus on normal scenarios
datasets = ['ghent', 'norway', 'NY', 'opennetlab']
sample_weights = 'uniform'

# Phase 2: Learn edge cases (Epochs 31-60)
# Oversample rare scenarios
sample_weights = {
    'loss > 0': 50x,
    'delay > 500ms': 10x,
    'normal': 1x
}

# Phase 3: Fine-tune robustness (Epochs 61-80)
# Focus on hardest scenarios
hard_files = loss_files + extreme_delay_files
```

---

## 📊 Recommended Evaluation Splits

### Option A: By Dataset (Recommended)
```python
train_datasets = ['ghent', 'norway', 'opennetlab']  # 80%
val_datasets = ['NY'][:5]                            # 10% 
test_datasets = ['NY'][5:]                           # 10%
```
- Pros: Tests generalization to new scenarios
- Cons: NY has best loss coverage, so train set lacks it

### Option B: By Scenario Type
```python
# Stratify by delay + loss characteristics
train = 80% from each scenario type
val = 10% from each type
test = 10% from each type

# Ensure balanced representation:
- Low delay + no loss
- High delay + no loss  
- Low delay + loss (oversample!)
- High delay + loss (oversample!)
```

### Option C: Temporal Split (for time-series models)
```python
# If using LSTM/GRU
# Split each file by time, not by files
train = first 80% of each trace
val = next 10%
test = last 10%
```

---

## 🚀 Next Steps

### Immediate Actions:
1. ✅ **Run coverage analysis** (DONE)
2. ⚠️ **Decide on handling packet loss gap**
   - Option A: Accept limitation, focus on delay-based control
   - Option B: Augment data with synthetic loss
   - Option C: Find additional real-world traces with loss
3. 📊 **Create balanced training set**
   - Implement dataset weighting
   - Oversample rare scenarios
4. 🎯 **Start with simple baseline** (Step 2)
   - Linear regression on current data
   - Measure performance by scenario type

### Before Training:
```bash
# 1. Extract samples with packet loss
python3 extract_loss_samples.py

# 2. Visualize key scenarios
python3 plot_gcc_data.py plot NY/rates_delay_loss_gcc_BusBrooklyn_bus57New.pickle
python3 plot_gcc_data.py plot opennetlab/rates_delay_loss_gcc_4G_3mbps.pickle

# 3. Create stratified splits
python3 create_train_splits.py --strategy balanced
```

---

## 📝 Conclusion

**You have:**
- ✅ Excellent delay coverage (especially norway & NY)
- ✅ Large dataset (898K samples)
- ✅ Diverse scenarios (urban, rural, various transport)

**You lack:**
- ❌ Sufficient packet loss scenarios (<1% non-zero)
- ❌ Sustained congestion events
- ⚠️ Balanced scenario distribution

**Impact on BC Training:**
- Your model will learn to **increase bandwidth well**
- But may **fail to handle packet loss properly**
- Risk of **over-aggressive** bandwidth probing
- Need **special attention** to loss handling during training

**Recommendation:** Proceed with training, but use **heavy oversampling** of packet loss scenarios and **weighted loss function**. Consider this a "bandwidth increase focused" BC model, not a full GCC replacement.
