#!/bin/bash
# Quick script to view all analysis results

echo "=================================="
echo "数据集覆盖分析 - 查看指南"
echo "=================================="
echo ""

# Check if files exist
if [ ! -f "docs/ANALYSIS_SUMMARY.md" ]; then
    echo "错误: 分析文件未找到"
    echo "请先运行: python3 tools/analyze_coverage.py"
    exit 1
fi

echo "已生成的分析文件:"
echo ""
echo "📄 文字报告:"
ls -lh docs/ANALYSIS_SUMMARY.md docs/COVERAGE_REPORT.md 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
echo ""
echo "📊 可视化图表:"
ls -lh reports/coverage_analysis.png reports/loss_analysis.png 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
echo ""

echo "=================================="
echo "快速查看命令:"
echo "=================================="
echo ""
echo "1. 中文快速总结:"
echo "   cat docs/ANALYSIS_SUMMARY.md | less"
echo ""
echo "2. 详细英文报告:"
echo "   cat docs/COVERAGE_REPORT.md | less"
echo ""
echo "3. 查看覆盖情况图表:"
echo "   xdg-open reports/coverage_analysis.png"
echo "   # 或: eog reports/coverage_analysis.png"
echo ""
echo "4. 查看丢包分析图表:"
echo "   xdg-open reports/loss_analysis.png"
echo ""
echo "=================================="
echo "关键发现:"
echo "=================================="
echo ""

# Extract key findings
echo "✅ 优势:"
echo "   • 总样本数: 897,909"
echo "   • 高延迟覆盖优秀 (norway: 46.93%, NY: 41.60%)"
echo "   • 多样化场景"
echo ""
echo "❌ 严重问题:"
echo "   • 丢包场景覆盖不足 (<1%样本有丢包)"
echo "   • 需要50倍过采样来平衡"
echo ""
echo "🎯 最有价值的文件:"
echo "   1. opennetlab/4G_3mbps.pickle (20.33%有丢包)"
echo "   2. NY/BusBrooklyn_bus57New.pickle (1.21%有丢包)"
echo "   3. NY/Ferry_Ferry4.pickle (1.57%有丢包)"
echo ""
echo "💡 建议:"
echo "   • 在训练时重采样高丢包文件 50倍"
echo "   • 使用加权损失函数"
echo "   • 重点评估极端场景的性能"
echo ""
echo "=================================="
echo "下一步:"
echo "=================================="
echo ""
echo "选项1: 查看中文总结"
echo "   cat docs/ANALYSIS_SUMMARY.md"
echo ""
echo "选项2: 查看详细报告"
echo "   cat docs/COVERAGE_REPORT.md"
echo ""
echo "选项3: 打开所有图表"
echo "   xdg-open reports/coverage_analysis.png reports/loss_analysis.png"
echo ""
echo "选项4: 开始数据准备"
echo "   # 创建平衡的训练数据集"
echo "   # 提取重点文件"
echo "   # 实现重采样策略"
echo ""

# Interactive menu
echo "=================================="
read -p "是否现在查看中文总结? (y/n): " response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    cat docs/ANALYSIS_SUMMARY.md | less
fi
