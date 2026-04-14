#!/bin/bash
# VoyageAgent 项目初始化脚本

echo "╔════════════════════════════════════════════════════════════╗"
echo "║      VoyageAgent - 智能旅行规划系统 - 初始化脚本           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 检查 Python 版本
echo "🔍 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.9 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ 发现 Python $PYTHON_VERSION"

# 创建虚拟环境
echo ""
echo "📦 创建 Python 虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "✓ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo ""
echo "🔌 激活虚拟环境..."
source venv/bin/activate
echo "✓ 虚拟环境已激活"

# 升级 pip
echo ""
echo "⬆️  升级 pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip 已升级"

# 安装依赖
echo ""
echo "📚 安装项目依赖..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ 依赖安装完成"

# 配置环境变量
echo ""
echo "⚙️  配置环境变量..."
if [ -f ".env" ]; then
    echo "⚠️  .env 文件已存在，跳过创建"
else
    cp .env.example .env
    echo "✓ .env 文件已创建"
    echo "   📝 请编辑 .env 文件，添加必要的 API 密钥"
fi

# 运行框架测试
echo ""
echo "🧪 运行框架完整性测试..."
python test_framework.py

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   初始化完成！                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 后续步骤："
echo "   1. 编辑 .env 文件配置必要的 API 密钥"
echo "   2. 运行测试: pytest tests/ -v"
echo "   3. 启动应用: python main.py"
echo ""
echo "📚 了解更多："
echo "   - 架构文档: docs/architecture.md"
echo "   - 项目文档: README.md"
echo "   - 框架报告: FRAMEWORK_REPORT.md"
echo ""
echo "🚀 祝开发顺利！"
