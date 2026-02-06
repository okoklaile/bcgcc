# BC-GCC Training Guide

## 项目结构

```
bc_gcc/
├── src/                   # 训练代码
│   ├── config.py         # 配置文件
│   ├── dataset.py        # 数据加载
│   ├── model.py          # LSTM模型
│   └── train.py          # 训练脚本
├── data/                  # 数据集
├── checkpoints/           # 模型检查点
├── logs/                  # Tensorboard日志
└── requirements.txt       # 依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置训练参数

编辑 `src/config.py` 修改训练参数：

```python
# 重要参数
WINDOW_SIZE = 10          # 时间窗口大小
LSTM_HIDDEN_SIZE = 128    # LSTM隐藏层大小
BATCH_SIZE = 256          # 批次大小
LEARNING_RATE = 1e-3      # 学习率
NUM_EPOCHS = 100          # 训练轮数
```

### 3. 开始训练

```bash
cd src
python train.py
```

### 4. 监控训练

```bash
tensorboard --logdir logs
```

然后访问: http://localhost:6006

## 模型架构

### 输入特征

**核心特征** (6个，用于BC训练):
- `delay`: 当前延迟 (ms)
- `loss_ratio`: 丢包率 (0-1)
- `receiving_rate`: 接收速率 (bps)
- `prev_bandwidth`: 上一时刻带宽预测 (bps)
- `delay_gradient`: 延迟变化率
- `throughput`: 实际吞吐量

**预留特征** (8个，为强化学习预留):
- `reward`: RL奖励信号
- `value_estimate`: RL价值函数
- `action_prob`: RL动作概率
- `advantage`: RL优势函数
- `custom_1` ~ `custom_4`: 自定义特征

**总特征维度**: 14

### 模型结构

```
Input: [batch, window_size, 14]
  ↓
LSTM (2 layers, 128 hidden)
  ↓
FC (128 → 64 → 32 → 1)
  ↓
Output: [batch, 1] (bandwidth prediction)
```

### 参数量

约 **620K** 可训练参数 (优化后，原始为155K)

## 数据处理

### 数据不平衡问题

数据集存在严重的丢包场景不足问题（<1%样本有丢包），解决方案：

1. **文件级重采样**
   - `4G_3mbps.pickle`: 50倍
   - `BusBrooklyn_bus57New.pickle`: 30倍
   - `Ferry_Ferry4.pickle`: 30倍
   - `7Train_7trainNew.pickle`: 20倍

2. **样本级加权**
   - 无丢包样本: 权重 1.0
   - 有丢包样本 (>1%): 权重 50.0
   - 高延迟样本 (>300ms): 权重 10.0

### 数据划分

- Train: 80% (约107个文件)
- Val: 10% (约13个文件)
- Test: 10% (约13个文件)

## 训练技巧

### 1. 梯度裁剪

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

防止梯度爆炸，特别是LSTM训练中很重要。

### 2. 学习率调度

使用ReduceLROnPlateau：
- 验证损失不下降5个epoch后，学习率减半
- 最小学习率: 1e-6

### 3. 混合精度训练 (AMP)

RTX 3090优化：使用FP16加速训练
- 速度提升30-50%
- 显存使用减少
- 无精度损失

### 4. 早停

验证损失不下降10个epoch后停止训练。

### 5. 损失函数

组合损失: `0.7 * MSE + 0.3 * MAPE`
- MSE: 适合大值预测
- MAPE: 关注相对误差

### 6. CuDNN Benchmark

自动选择最优卷积算法，提升训练速度。

## 评估指标

- **MAE** (Mean Absolute Error): 平均绝对误差 (bps)
- **MAPE** (Mean Absolute Percentage Error): 平均百分比误差
- **R²**: 决定系数，衡量拟合优度
- **分场景评估**: 
  - 零丢包场景
  - 有丢包场景
  - 高延迟场景

## 预期结果

### 性能指标
基于数据集特点，预期性能：

- **整体R²**: 0.7 - 0.85 (优化后可能更高)
- **零丢包场景**: R² > 0.85 (数据充足)
- **有丢包场景**: R² 0.5 - 0.7 (数据有限)
- **平均MAE**: 100K - 300K bps (0.1 - 0.3 Mbps)

### 训练速度 (RTX 3090)
- **每个epoch**: 0.4 - 0.7秒
- **100 epochs**: < 1分钟
- **GPU利用率**: 85-100%
- **显存使用**: ~4GB / 25GB

## 常见问题

### Q1: 训练很慢怎么办？

**A:** 
- 减少 `BATCH_SIZE`
- 使用GPU（设置 `DEVICE = 'cuda'`）
- 减少 `NUM_EPOCHS`

### Q2: 验证损失不下降？

**A:**
- 检查学习率是否太大/太小
- 增加 `DROPOUT` 防止过拟合
- 检查数据是否正确归一化

### Q3: 模型在丢包场景表现差？

**A:**
- 增加重采样倍数
- 增加样本权重
- 考虑数据增强

### Q4: 如何用于强化学习？

**A:**
模型已预留8个特征位：
1. 加载训练好的BC模型
2. 在RL训练时，填充预留特征（reward, value等）
3. Fine-tune整个模型或只训练新增的层

## 下一步

1. **基础训练**: 完成BC训练，评估baseline性能
2. **分析错误**: 分析模型在哪些场景下表现差
3. **数据增强**: 如果丢包场景性能不佳，考虑合成数据
4. **强化学习**: 使用BC模型作为初始化，进行在线RL fine-tuning

## 文件说明

- `checkpoints/best.pt`: 最佳模型（按验证损失）
- `checkpoints/latest.pt`: 最新模型
- `logs/`: Tensorboard日志
  - `train/batch_loss`: 每批次训练损失
  - `train/epoch_loss`: 每轮训练损失
  - `val/loss`: 验证损失
  - `val/mae`: 验证MAE
  - `val/r2`: 验证R²

## 参考

- GCC算法: RFC 8298
- 行为克隆: Imitation Learning相关论文
- 强化学习: PPO, SAC等算法
