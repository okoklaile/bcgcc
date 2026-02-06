#!/usr/bin/env python3
"""
查看WebRTC GCC pickle文件内容的工具脚本
"""
import pickle
import sys
import os
from pathlib import Path
import json

def view_pickle(file_path):
    """读取并显示pickle文件的内容"""
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        print(f"\n{'='*80}")
        print(f"文件: {file_path}")
        print(f"{'='*80}\n")
        
        # 显示数据类型
        print(f"数据类型: {type(data)}")
        print(f"{'='*80}\n")
        
        # 根据数据类型显示内容
        if isinstance(data, dict):
            print("字典内容:")
            print(f"键的数量: {len(data)}")
            print(f"键列表: {list(data.keys())}\n")
            
            for key, value in data.items():
                print(f"\n键: {key}")
                print(f"  类型: {type(value)}")
                
                if isinstance(value, (list, tuple)):
                    print(f"  长度: {len(value)}")
                    if len(value) > 0:
                        print(f"  首个元素: {value[0]}")
                        if len(value) > 1:
                            print(f"  最后元素: {value[-1]}")
                        if len(value) <= 10:
                            print(f"  所有元素: {value}")
                elif isinstance(value, (int, float, str, bool)):
                    print(f"  值: {value}")
                else:
                    print(f"  内容: {value}")
                    
        elif isinstance(data, (list, tuple)):
            print(f"列表/元组内容:")
            print(f"长度: {len(data)}")
            if len(data) > 0:
                print(f"首个元素: {data[0]}")
                if len(data) > 1:
                    print(f"最后元素: {data[-1]}")
                if len(data) <= 20:
                    print(f"\n所有元素:")
                    for i, item in enumerate(data):
                        print(f"  [{i}]: {item}")
        else:
            print(f"内容: {data}")
            
        return data
        
    except Exception as e:
        print(f"错误: 无法读取文件 {file_path}")
        print(f"错误信息: {str(e)}")
        return None

def list_pickle_files(directory='.', pattern='*.pickle'):
    """列出目录中的所有pickle文件"""
    path = Path(directory)
    pickle_files = sorted(path.rglob(pattern))
    
    print(f"\n在 {directory} 中找到 {len(pickle_files)} 个pickle文件:\n")
    
    # 按目录分组
    by_dir = {}
    for pf in pickle_files:
        dir_name = pf.parent.name
        if dir_name not in by_dir:
            by_dir[dir_name] = []
        by_dir[dir_name].append(pf.name)
    
    for dir_name, files in sorted(by_dir.items()):
        print(f"\n{dir_name}/ ({len(files)} 个文件)")
        for f in sorted(files)[:5]:  # 只显示前5个
            print(f"  - {f}")
        if len(files) > 5:
            print(f"  ... 还有 {len(files)-5} 个文件")
    
    return pickle_files

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print(f"  {sys.argv[0]} <pickle文件路径>  # 查看单个文件")
        print(f"  {sys.argv[0]} list              # 列出所有pickle文件")
        print(f"  {sys.argv[0]} list <目录>       # 列出指定目录的pickle文件")
        print("\n示例:")
        print(f"  {sys.argv[0]} ghent/rates_delay_loss_gcc_report_bicycle_0001.pickle")
        print(f"  {sys.argv[0]} list")
        print(f"  {sys.argv[0]} list ghent/")
        sys.exit(1)
    
    if sys.argv[1] == 'list':
        directory = sys.argv[2] if len(sys.argv) > 2 else '.'
        list_pickle_files(directory)
    else:
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"错误: 文件 {file_path} 不存在")
            sys.exit(1)
        view_pickle(file_path)

if __name__ == '__main__':
    main()
