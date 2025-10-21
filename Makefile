.PHONY: help install install-dev test test-basic test-paid test-all test-cov clean clean-all lint format check build upload docs

# 默认目标
.DEFAULT_GOAL := help

PYTHON := python
PIP := pip
PROJECT_NAME := ai_news_collector_lib
VENV := venv

# 颜色输出
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

## 帮助
help:
	@echo "$(BLUE)================================$(NC)"
	@echo "$(BLUE)AI News Collector - Makefile$(NC)"
	@echo "$(BLUE)================================$(NC)"
	@echo ""
	@echo "$(GREEN)安装相关:$(NC)"
	@echo "  make install          - 安装项目依赖"
	@echo "  make install-dev      - 安装开发依赖"
	@echo ""
	@echo "$(GREEN)测试相关:$(NC)"
	@echo "  make test             - 运行所有测试"
	@echo "  make test-basic       - 运行基础测试 (快速)"
	@echo "  make test-paid        - 运行付费API测试"
	@echo "  make test-cov         - 运行测试并生成覆盖率报告"
	@echo ""
	@echo "$(GREEN)代码质量:$(NC)"
	@echo "  make lint             - 运行flake8代码检查"
	@echo "  make format           - 使用black格式化代码"
	@echo "  make check            - 检查代码风格 (lint + type check)"
	@echo ""
	@echo "$(GREEN)清理相关:$(NC)"
	@echo "  make clean            - 删除临时文件和缓存"
	@echo "  make clean-all        - 删除所有生成的文件（包括venv和dist）"
	@echo ""
	@echo "$(GREEN)构建和发布:$(NC)"
	@echo "  make build            - 构建分发包"
	@echo "  make upload           - 上传到PyPI"
	@echo "  make upload-test      - 上传到TestPyPI"
	@echo ""
	@echo "$(GREEN)文档:$(NC)"
	@echo "  make docs             - 显示文档信息"
	@echo ""

## 安装依赖
install:
	@echo "$(BLUE)安装项目依赖...$(NC)"
	$(PIP) install -r requirements.txt

install-dev:
	@echo "$(BLUE)安装开发依赖...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio pytest-cov flake8 black

## 测试相关
test: test-all
	@echo "$(GREEN)✓ 所有测试完成$(NC)"

test-basic:
	@echo "$(BLUE)运行基础测试...$(NC)"
	$(PYTHON) -m pytest tests/test_integration_basic.py tests/test_integration_advanced.py -v

test-paid:
	@echo "$(BLUE)运行付费API测试...$(NC)"
	$(PYTHON) -m pytest tests/test_paid_apis.py -v

test-all:
	@echo "$(BLUE)运行所有测试...$(NC)"
	$(PYTHON) -m pytest tests/ -v

test-cov:
	@echo "$(BLUE)运行测试并生成覆盖率报告...$(NC)"
	$(PYTHON) -m pytest tests/ -v --cov=$(PROJECT_NAME) --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "$(GREEN)✓ HTML覆盖率报告生成到: htmlcov/index.html$(NC)"

## 代码质量
lint:
	@echo "$(BLUE)运行flake8代码检查...$(NC)"
	flake8 $(PROJECT_NAME) tests --max-line-length=88 --extend-ignore=E203,W503
	@echo "$(GREEN)✓ 代码检查通过$(NC)"

format:
	@echo "$(BLUE)使用black格式化代码...$(NC)"
	black $(PROJECT_NAME) tests --line-length=88
	@echo "$(GREEN)✓ 代码格式化完成$(NC)"

check: lint
	@echo "$(BLUE)运行完整检查...$(NC)"
	@echo "$(GREEN)✓ 所有检查通过$(NC)"

## 清理
clean:
	@echo "$(BLUE)清理临时文件和缓存...$(NC)"
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf $(PROJECT_NAME)/__pycache__ $(PROJECT_NAME)/*/__pycache__
	rm -rf tests/__pycache__ 
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ 清理完成$(NC)"

clean-all: clean
	@echo "$(BLUE)清理所有生成的文件...$(NC)"
	rm -rf build dist *.egg-info $(PROJECT_NAME).egg-info
	rm -rf $(VENV)
	@echo "$(GREEN)✓ 完全清理完成$(NC)"

## 构建和发布
build: clean
	@echo "$(BLUE)构建分发包...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ 构建完成$(NC)"
	@ls -lh dist/

upload: build
	@echo "$(YELLOW)准备上传到PyPI...$(NC)"
	@echo "确保已配置 ~/.pypirc，然后执行: twine upload dist/*"
	twine upload dist/*

upload-test: build
	@echo "$(YELLOW)上传到TestPyPI...$(NC)"
	twine upload --repository testpypi dist/*

## 文档
docs:
	@echo "$(BLUE)================================$(NC)"
	@echo "$(BLUE)文档信息$(NC)"
	@echo "$(BLUE)================================$(NC)"
	@echo ""
	@echo "$(GREEN)主要文档:$(NC)"
	@echo "  - README.md                        - 项目说明"
	@echo "  - USAGE_GUIDE.md                   - 使用指南"
	@echo "  - TESTING_GUIDE.md                 - 测试指南"
	@echo "  - ARCHITECTURE.md                  - 架构说明"
	@echo "  - CHANGELOG.md                     - 更新日志"
	@echo ""
	@echo "$(GREEN)进阶文档 (docs/ 目录):$(NC)"
	@echo "  - CI_CD_GITHUB_ACTIONS_GUIDE.md   - GitHub Actions CI/CD"
	@echo "  - PAID_API_TESTING_GUIDE.md       - 付费API测试指南"
	@echo "  - QUICK_START_CI_CD.md            - CI/CD快速开始"
	@echo ""
	@echo "$(GREEN)发布相关:$(NC)"
	@echo "  - CRITICAL_FIXES_v0.1.2.md        - v0.1.2关键修复"
	@echo "  - QUICK_RELEASE.md                - 快速发布指南"
	@echo "  - RELEASE_GUIDE.md                - 完整发布流程"
	@echo ""

## 快速开发流程
dev-setup: install-dev
	@echo "$(GREEN)✓ 开发环境配置完成$(NC)"
	@echo "$(YELLOW)建议下一步:$(NC)"
	@echo "  1. make check      - 检查代码质量"
	@echo "  2. make test       - 运行所有测试"
	@echo "  3. make format     - 格式化代码"

dev-test: format lint test
	@echo "$(GREEN)✓ 开发前检查完成$(NC)"

# 特殊命令
.PHONY: venv
venv:
	@echo "$(BLUE)创建虚拟环境...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ 虚拟环境创建完成$(NC)"
	@echo "激活虚拟环境:"
	@echo "  Windows: $(VENV)\\Scripts\\activate"
	@echo "  Linux/Mac: source $(VENV)/bin/activate"
