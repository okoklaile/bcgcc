# WebRTC GCC 数据分析 - 快速参考

## 🚀 快速开始

```bash
# 1. 运行快速入门脚本
./quick_start.sh

# 2. 列出所有文件
python3 view_pickle.py list

# 3. 分析一个文件
python3 analyze_gcc_data.py analyze ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle
```

## 📊 常用命令

### 查看文件内容

```bash
# 列出所有pickle文件
python3 view_pickle.py list

# 列出特定目录
python3 view_pickle.py list ghent/

# 查看单个文件内容
python3 view_pickle.py ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle
```

### 数据分析

```bash
# 分析单个文件
python3 analyze_gcc_data.py analyze <文件路径>

# 对比多个文件
python3 analyze_gcc_data.py compare <文件1> <文件2> <文件3>

# 批量分析整个目录
python3 analyze_gcc_data.py batch-analyze ghent/

# 导出为CSV
python3 analyze_gcc_data.py export <文件路径> [输出.csv]
```

### 数据可视化

```bash
# 绘制单文件图表
python3 plot_gcc_data.py plot <文件路径>

# 保存图表
python3 plot_gcc_data.py plot <文件路径> output.png

# 对比多个文件
python3 plot_gcc_data.py compare <文件1> <文件2> <文件3> [output.png]

# 延迟分布图
python3 plot_gcc_data.py delay-dist <文件1> <文件2> [output.png]
```

## 📁 数据集说明

| 数据集 | 文件数 | 场景 |
|--------|--------|------|
| **ghent/** | 40 | bicycle, bus, car, tram, train, metro 等移动场景 |
| **norway/** | 59 | bus, ferry 等不同时间段数据 |
| **NY/** | 25 | 纽约地铁和公交 |
| **opennetlab/** | 9 | 4G/5G 不同带宽场景 |

## 🔍 数据字段说明

每个pickle文件包含的数据：

```python
{
    'trace_name': str,              # 跟踪名称
    'bandwidth_prediction': list,    # 带宽预测 (bps)
    'sending_rate': list,            # 发送速率 (bps)
    'receiving_rate': list,          # 接收速率 (bps)
    'delay': list,                   # 延迟 (ms)
    'loss_ratio': list               # 丢包率 (0-1)
}
```

## 💡 使用场景示例

### 场景1: 对比不同交通方式的网络性能

```bash
python3 analyze_gcc_data.py compare \
    ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle \
    ghent/rates_delay_loss_gcc_report_bus_0001.pickle \
    ghent/rates_delay_loss_gcc_report_car_0001.pickle
```

### 场景2: 分析4G vs 5G性能差异

```bash
python3 analyze_gcc_data.py compare \
    opennetlab/rates_delay_loss_gcc_4G_*.pickle \
    opennetlab/rates_delay_loss_gcc_5G_*.pickle
```

### 场景3: 批量导出数据进行Excel分析

```bash
# 导出ghent目录所有数据
for file in ghent/*.pickle; do
    python3 analyze_gcc_data.py export "$file"
done

# 所有CSV文件将在同目录生成
ls ghent/*.csv
```

### 场景4: 生成报告图表

```bash
# 单个场景详细分析
python3 plot_gcc_data.py plot \
    ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle \
    reports/bicycle_analysis.png

# 多场景对比
python3 plot_gcc_data.py compare \
    ghent/rates_delay_loss_gcc_report_*_0001.pickle \
    reports/scenarios_comparison.png
```

## 📈 关键性能指标

### 带宽利用率
- **计算**: sending_rate / bandwidth_prediction × 100%
- **理想值**: 90-100%（充分利用但不过载）
- **过高**: >100% 表示发送速率超过预测，可能导致拥塞
- **过低**: <80% 表示利用不足

### 延迟稳定性
- **指标**: 延迟的标准差
- **理想值**: 标准差 < 50ms
- **问题**: 标准差 > 100ms 表示网络抖动严重

### 丢包率
- **理想值**: < 1%
- **可接受**: 1-5%
- **严重**: > 5% 会明显影响通话质量

## 🔧 Python代码示例

### 基础读取和分析

```python
import pickle
import numpy as np

# 读取数据
with open('ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle', 'rb') as f:
    data = pickle.load(f)

# 计算统计值
avg_bandwidth = np.mean(data['bandwidth_prediction']) / 1e6  # Mbps
avg_delay = np.mean(data['delay'])
avg_loss = np.mean(data['loss_ratio']) * 100  # %

print(f"平均带宽: {avg_bandwidth:.2f} Mbps")
print(f"平均延迟: {avg_delay:.2f} ms")
print(f"平均丢包率: {avg_loss:.4f}%")
```

### 计算带宽利用率

```python
import numpy as np

bw_pred = np.array(data['bandwidth_prediction'])
send_rate = np.array(data['sending_rate'])

# 避免除零
bw_pred_safe = np.where(bw_pred > 0, bw_pred, 1)
utilization = (send_rate / bw_pred_safe) * 100

print(f"平均利用率: {np.mean(utilization):.2f}%")
print(f"利用率范围: {np.min(utilization):.2f}% - {np.max(utilization):.2f}%")
```

### 找出延迟峰值时刻

```python
import numpy as np

delays = np.array(data['delay'])
threshold = np.percentile(delays, 95)  # 95th百分位

peak_indices = np.where(delays > threshold)[0]
print(f"发现 {len(peak_indices)} 个高延迟时刻（>{threshold:.2f}ms）")

for idx in peak_indices[:10]:  # 显示前10个
    print(f"  时刻 {idx*0.2:.1f}s: {delays[idx]:.2f}ms")
```

## 🛠️ 故障排查

### 问题1: 无法读取pickle文件
```bash
# 检查文件是否存在
ls -lh ghent/*.pickle

# 验证Python版本
python3 --version

# 测试pickle读取
python3 -c "import pickle; print('OK')"
```

### 问题2: 缺少依赖
```bash
# 安装所有依赖
pip install numpy matplotlib

# 验证安装
python3 -c "import numpy, matplotlib; print('所有依赖已安装')"
```

### 问题3: 可视化无法显示
```bash
# 改为保存图片而不是显示
python3 plot_gcc_data.py plot <文件> output.png

# 或者安装tkinter
sudo apt-get install python3-tk
```

## 📚 更多资源

- **详细文档**: `README.md`
- **快速开始**: `./quick_start.sh`
- **数据分析**: `analyze_gcc_data.py`
- **可视化**: `plot_gcc_data.py`
- **查看工具**: `view_pickle.py`

## 💬 常见问题

**Q: 数据采集频率是多少？**
A: 默认是200ms（0.2秒）一个数据点

**Q: 带宽单位是什么？**
A: bps (bits per second)，除以1e6转换为Mbps

**Q: 如何找到特定场景的数据？**
A: 使用 `python3 view_pickle.py list` 查看所有文件，然后根据文件名选择

**Q: 可以用Excel分析吗？**
A: 可以！使用 `analyze_gcc_data.py export` 导出为CSV后用Excel打开

**Q: 如何批量处理所有文件？**
A: 使用bash循环或 `batch-analyze` 命令
