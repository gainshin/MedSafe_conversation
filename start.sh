#!/bin/bash

# MediNote-AI 老年人安全醫療對話框架
# 啟動腳本

set -e

echo "🚀 啟動 MediNote-AI 老年人安全醫療對話框架"
echo "=============================================="

# 檢查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝，請先安裝 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [[ "$PYTHON_VERSION" < "$REQUIRED_VERSION" ]]; then
    echo "❌ Python 版本過低，需要 Python 3.8+，目前版本: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python 版本檢查通過: $PYTHON_VERSION"

# 檢查依賴
echo "📦 檢查依賴套件..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 不存在"
    exit 1
fi

# 安裝依賴
echo "📥 安裝依賴套件..."
pip3 install -r requirements.txt --quiet

# 設定環境變數
echo "⚙️  設定環境變數..."
if [ ! -f "config/.env" ]; then
    echo "⚠️  未找到 config/.env，使用預設配置"
    export FLASK_ENV=development
    export FLASK_DEBUG=true
    export SECRET_KEY=dev-secret-key-$(date +%s)
fi

# 建立必要的目錄
echo "📁 建立必要的目錄..."
mkdir -p logs
mkdir -p tests/reports

# 執行系統測試
echo "🧪 執行系統測試..."
if python3 test_system_simple.py; then
    echo "✅ 系統測試通過"
else
    echo "⚠️  系統測試有部分失敗，但系統仍可運行"
fi

# 啟動服務
echo "🚀 啟動 Flask 服務..."
echo "服務將在 http://localhost:5000 提供"
echo "按 Ctrl+C 停止服務"
echo ""

python3 src/main.py

echo ""
echo "🛑 服務已停止"
echo "感謝使用 MediNote-AI 老年人安全醫療對話框架！"