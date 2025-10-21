#!/bin/bash
# 付费API测试快速运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "  付费API测试工具"
echo "=========================================="
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在"
    echo ""
    echo "请创建 .env 文件并配置API密钥："
    echo "  cp env.example .env"
    echo ""
    exit 1
fi

# 检查是否有cassettes
CASSETTE_DIR="$PROJECT_ROOT/tests/cassettes"
CASSETTE_COUNT=0
if [ -d "$CASSETTE_DIR" ]; then
    CASSETTE_COUNT=$(find "$CASSETTE_DIR" -name "*.yaml" -type f | wc -l)
fi

echo "📊 当前状态："
echo "  Cassette文件: $CASSETTE_COUNT 个"
echo ""

# 显示菜单
echo "请选择操作："
echo ""
echo "  1) 首次录制 - 运行付费API测试并录制HTTP请求（消耗少量API配额）"
echo "  2) 离线测试 - 使用现有cassettes运行（完全免费）"
echo "  3) 重新录制 - 删除旧cassettes并重新录制"
echo "  4) 查看覆盖率 - 运行测试并生成覆盖率报告"
echo "  5) 仅测试特定API"
echo "  0) 退出"
echo ""
read -p "请输入选项 [0-5]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 开始首次录制..."
        echo ""
        
        # 检查必要的环境变量
        if ! grep -q "^ALLOW_NETWORK=1" .env; then
            echo "⚠️  请在 .env 中设置 ALLOW_NETWORK=1"
            exit 1
        fi
        
        if ! grep -q "^TEST_PAID_APIS=1" .env; then
            echo "⚠️  请在 .env 中设置 TEST_PAID_APIS=1"
            exit 1
        fi
        
        echo "✅ 环境配置正确"
        echo ""
        echo "💰 注意：这将消耗少量API配额（约 <$0.01）"
        echo ""
        read -p "确认继续? [y/N] " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            echo "已取消"
            exit 0
        fi
        
        python -m pytest tests/test_paid_apis.py -v
        
        echo ""
        echo "✅ 录制完成！后续可以离线运行测试"
        ;;
        
    2)
        echo ""
        echo "🏃 运行离线测试..."
        echo ""
        
        if [ $CASSETTE_COUNT -eq 0 ]; then
            echo "❌ 错误：没有找到cassette文件"
            echo ""
            echo "请先运行选项1进行首次录制"
            exit 1
        fi
        
        python -m pytest tests/test_paid_apis.py -v
        
        echo ""
        echo "✅ 测试完成！完全使用cassette回放，零API消耗"
        ;;
        
    3)
        echo ""
        echo "🔄 重新录制cassettes..."
        echo ""
        
        if [ $CASSETTE_COUNT -gt 0 ]; then
            read -p "确认删除 $CASSETTE_COUNT 个现有cassettes? [y/N] " confirm
            if [[ ! $confirm =~ ^[Yy]$ ]]; then
                echo "已取消"
                exit 0
            fi
            
            rm -f "$CASSETTE_DIR"/*.yaml
            echo "✅ 已删除旧cassettes"
        fi
        
        # 临时设置 UPDATE_CASSETTES
        export UPDATE_CASSETTES=1
        
        python -m pytest tests/test_paid_apis.py -v
        
        echo ""
        echo "✅ 重新录制完成！"
        ;;
        
    4)
        echo ""
        echo "📊 生成覆盖率报告..."
        echo ""
        
        python -m pytest tests/test_paid_apis.py \
            --cov=ai_news_collector_lib \
            --cov-report=term-missing \
            --cov-report=html \
            -v
        
        echo ""
        echo "✅ 覆盖率报告已生成"
        echo ""
        echo "📄 查看详细报告："
        echo "  htmlcov/index.html"
        ;;
        
    5)
        echo ""
        echo "可用的API测试："
        echo ""
        echo "  1) Tavily"
        echo "  2) Google Search"
        echo "  3) Serper"
        echo "  4) Brave Search"
        echo "  5) MetaSota"
        echo "  6) NewsAPI"
        echo ""
        read -p "请输入API编号 [1-6]: " api_choice
        
        case $api_choice in
            1) TEST_NAME="test_tavily_search" ;;
            2) TEST_NAME="test_google_search" ;;
            3) TEST_NAME="test_serper_search" ;;
            4) TEST_NAME="test_brave_search" ;;
            5) TEST_NAME="test_metasota_search" ;;
            6) TEST_NAME="test_newsapi_search" ;;
            *)
                echo "❌ 无效选项"
                exit 1
                ;;
        esac
        
        echo ""
        echo "🧪 运行测试: $TEST_NAME"
        echo ""
        
        python -m pytest "tests/test_paid_apis.py::$TEST_NAME" -v
        ;;
        
    0)
        echo "退出"
        exit 0
        ;;
        
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "  完成"
echo "=========================================="
