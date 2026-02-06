#!/bin/bash
# WebRTC GCC数据分析快速入门脚本

echo "================================"
echo "WebRTC GCC 数据分析工具"
echo "================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要安装Python 3"
    exit 1
fi

echo "✓ Python 3 已安装"

# 检查numpy
python3 -c "import numpy" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ numpy 已安装"
else
    echo "✗ numpy 未安装"
    echo "  安装命令: pip install numpy"
fi

# 检查matplotlib
python3 -c "import matplotlib" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ matplotlib 已安装（可视化功能可用）"
else
    echo "✗ matplotlib 未安装（可视化功能不可用）"
    echo "  安装命令: pip install matplotlib"
fi

echo ""
echo "================================"
echo "数据集统计"
echo "================================"
echo ""

# 统计各目录文件数
for dir in data/ghent data/norway data/NY data/opennetlab; do
    if [ -d "$dir" ]; then
        count=$(ls -1 "$dir"/*.pickle 2>/dev/null | wc -l)
        dirname=$(basename "$dir")
        echo "$dirname: $count 个文件"
    fi
done

echo ""
echo "================================"
echo "快速示例"
echo "================================"
echo ""

# 选择一个示例文件
EXAMPLE_FILE=$(find data/ -name "*.pickle" -type f | head -1)

if [ -n "$EXAMPLE_FILE" ]; then
    echo "1. 查看文件基本信息："
    echo "   python3 tools/view_pickle.py \"$EXAMPLE_FILE\""
    echo ""
    
    echo "2. 详细分析："
    echo "   python3 tools/analyze_gcc_data.py analyze \"$EXAMPLE_FILE\""
    echo ""
    
    echo "3. 导出为CSV："
    echo "   python3 tools/analyze_gcc_data.py export \"$EXAMPLE_FILE\" outputs/output.csv"
    echo ""
    
    echo "4. 可视化（需要matplotlib）："
    echo "   python3 tools/plot_gcc_data.py plot \"$EXAMPLE_FILE\" reports/output.png"
    echo ""
    
    echo "是否要运行示例分析？(y/n)"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo ""
        echo "运行示例分析..."
        echo ""
        python3 tools/analyze_gcc_data.py analyze "$EXAMPLE_FILE"
    fi
else
    echo "未找到pickle文件"
fi

echo ""
echo "================================"
echo "更多信息请查看 README.md"
echo "================================"
