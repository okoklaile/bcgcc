#!/usr/bin/env python3
"""
WebRTC GCC数据分析工具
提供统计分析、数据对比和可视化功能
"""
import pickle
import sys
import os
from pathlib import Path
import numpy as np

def load_pickle(file_path):
    """加载pickle文件"""
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"错误: 无法读取文件 {file_path}: {e}")
        return None

def analyze_file(file_path):
    """分析单个文件的统计信息"""
    data = load_pickle(file_path)
    if data is None:
        return
    
    print(f"\n{'='*80}")
    print(f"文件分析: {file_path}")
    print(f"{'='*80}\n")
    
    if 'trace_name' in data:
        print(f"跟踪名称: {data['trace_name']}")
    
    print(f"\n数据点数量: {len(data.get('bandwidth_prediction', []))}")
    
    # 分析每个指标
    metrics = {
        'bandwidth_prediction': '带宽预测 (bps)',
        'sending_rate': '发送速率 (bps)',
        'receiving_rate': '接收速率 (bps)',
        'delay': '延迟 (ms)',
        'loss_ratio': '丢包率'
    }
    
    print(f"\n{'指标':<20} {'最小值':<15} {'最大值':<15} {'平均值':<15} {'中位数':<15}")
    print('-' * 80)
    
    for key, label in metrics.items():
        if key in data and len(data[key]) > 0:
            values = np.array(data[key])
            min_val = np.min(values)
            max_val = np.max(values)
            mean_val = np.mean(values)
            median_val = np.median(values)
            
            print(f"{label:<20} {min_val:<15.2f} {max_val:<15.2f} {mean_val:<15.2f} {median_val:<15.2f}")
    
    # 带宽利用率分析
    if 'bandwidth_prediction' in data and 'sending_rate' in data:
        bw_pred = np.array(data['bandwidth_prediction'])
        send_rate = np.array(data['sending_rate'])
        
        # 避免除零
        bw_pred_safe = np.where(bw_pred > 0, bw_pred, 1)
        utilization = (send_rate / bw_pred_safe) * 100
        
        print(f"\n带宽利用率统计:")
        print(f"  平均利用率: {np.mean(utilization):.2f}%")
        print(f"  中位数利用率: {np.median(utilization):.2f}%")
        print(f"  最大利用率: {np.max(utilization):.2f}%")
        print(f"  最小利用率: {np.min(utilization):.2f}%")
    
    # 延迟和丢包分析
    if 'delay' in data:
        delays = np.array(data['delay'])
        print(f"\n延迟分析:")
        print(f"  标准差: {np.std(delays):.2f} ms")
        print(f"  99th百分位: {np.percentile(delays, 99):.2f} ms")
        
    if 'loss_ratio' in data:
        losses = np.array(data['loss_ratio'])
        print(f"\n丢包分析:")
        print(f"  平均丢包率: {np.mean(losses)*100:.4f}%")
        print(f"  最大丢包率: {np.max(losses)*100:.4f}%")
        print(f"  非零丢包点数: {np.count_nonzero(losses)}/{len(losses)}")

def compare_files(file_paths):
    """对比多个文件"""
    print(f"\n{'='*80}")
    print(f"对比 {len(file_paths)} 个文件")
    print(f"{'='*80}\n")
    
    all_data = []
    for fp in file_paths:
        data = load_pickle(fp)
        if data:
            all_data.append((Path(fp).name, data))
    
    if not all_data:
        print("没有可用的数据进行对比")
        return
    
    # 对比表格
    print(f"{'文件名':<50} {'平均延迟(ms)':<15} {'平均丢包率(%)':<15} {'平均带宽(Mbps)':<15}")
    print('-' * 95)
    
    for name, data in all_data:
        avg_delay = np.mean(data.get('delay', [0])) if 'delay' in data else 0
        avg_loss = np.mean(data.get('loss_ratio', [0])) * 100 if 'loss_ratio' in data else 0
        avg_bw = np.mean(data.get('bandwidth_prediction', [0])) / 1e6 if 'bandwidth_prediction' in data else 0
        
        print(f"{name:<50} {avg_delay:<15.2f} {avg_loss:<15.4f} {avg_bw:<15.2f}")

def export_to_csv(file_path, output_path=None):
    """导出pickle数据到CSV文件"""
    data = load_pickle(file_path)
    if data is None:
        return
    
    if output_path is None:
        output_path = file_path.replace('.pickle', '.csv')
    
    try:
        import csv
        
        # 准备数据
        keys = ['bandwidth_prediction', 'sending_rate', 'receiving_rate', 'delay', 'loss_ratio']
        rows = []
        
        max_len = max(len(data.get(k, [])) for k in keys)
        
        for i in range(max_len):
            row = {'index': i}
            for key in keys:
                if key in data and i < len(data[key]):
                    row[key] = data[key][i]
                else:
                    row[key] = ''
            rows.append(row)
        
        # 写入CSV
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['index'] + keys)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"\n成功导出到: {output_path}")
        print(f"共 {len(rows)} 行数据")
        
    except Exception as e:
        print(f"导出失败: {e}")

def main():
    if len(sys.argv) < 2:
        print("WebRTC GCC数据分析工具")
        print("\n使用方法:")
        print(f"  {sys.argv[0]} analyze <文件>        # 分析单个文件")
        print(f"  {sys.argv[0]} compare <文件1> <文件2> ...  # 对比多个文件")
        print(f"  {sys.argv[0]} export <文件> [输出.csv]     # 导出为CSV")
        print(f"  {sys.argv[0]} batch-analyze <目录>   # 批量分析目录中的所有文件")
        print("\n示例:")
        print(f"  {sys.argv[0]} analyze ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle")
        print(f"  {sys.argv[0]} compare ghent/*.pickle")
        print(f"  {sys.argv[0]} export ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle")
        print(f"  {sys.argv[0]} batch-analyze ghent/")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'analyze':
        if len(sys.argv) < 3:
            print("错误: 需要指定文件路径")
            sys.exit(1)
        analyze_file(sys.argv[2])
    
    elif command == 'compare':
        if len(sys.argv) < 3:
            print("错误: 需要至少一个文件路径")
            sys.exit(1)
        compare_files(sys.argv[2:])
    
    elif command == 'export':
        if len(sys.argv) < 3:
            print("错误: 需要指定文件路径")
            sys.exit(1)
        output = sys.argv[3] if len(sys.argv) > 3 else None
        export_to_csv(sys.argv[2], output)
    
    elif command == 'batch-analyze':
        if len(sys.argv) < 3:
            print("错误: 需要指定目录路径")
            sys.exit(1)
        directory = sys.argv[2]
        pickle_files = sorted(Path(directory).glob('*.pickle'))
        print(f"\n在 {directory} 中找到 {len(pickle_files)} 个文件")
        for pf in pickle_files:
            analyze_file(str(pf))
            print("\n")
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
