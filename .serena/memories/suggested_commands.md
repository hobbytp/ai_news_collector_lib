# 推荐命令和工作流

## 环境设置

### 创建虚拟环境
```bash
python -m venv venv
```

### 激活虚拟环境
```bash
# Windows (Git Bash)
source venv/Scripts/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Linux/macOS
source venv/bin/activate
```

### 安装依赖

```bash
# 基础依赖
pip install -r requirements.txt

# 开发依赖（含测试和代码质量工具）
pip install -e ".[dev]"

# 完整依赖（包括所有可选功能）
pip install -e ".[advanced,nlp,web,dev]"
```

## 开发工作流

### 1. 代码格式化

```bash
# 检查格式
black --check ai_news_collector_lib/

# 自动格式化
black ai_news_collector_lib/
```

### 2. 代码检查

```bash
# Flake8 检查
flake8 ai_news_collector_lib/

# mypy 类型检查
mypy ai_news_collector_lib/ --strict
```

### 3. 测试运行

```bash
# 运行所有测试
pytest -v

# 运行特定测试文件
pytest tests/test_collector.py -v

# 运行特定测试
pytest tests/test_collector.py::TestAINewsCollector::test_initialization -v

# 显示覆盖率
pytest --cov=ai_news_collector_lib -v

# 只运行单元测试
pytest -m "not integration" -v

# 只运行集成测试
pytest -m integration -v

# 跳过慢速测试
pytest -m "not slow" -v

# VCR 录制/回放（网络测试）
ALLOW_NETWORK=1 pytest -m network -v         # 首次录制
UPDATE_CASSETTES=1 ALLOW_NETWORK=1 pytest -m network -v  # 更新磁带
pytest -m network -v                         # 离线回放
```

### 4. 完整开发循环

```bash
# 1. 格式化代码
black ai_news_collector_lib/

# 2. 检查代码
flake8 ai_news_collector_lib/

# 3. 类型检查
mypy ai_news_collector_lib/ --strict

# 4. 运行测试
pytest -v

# 5. 显示覆盖率
pytest --cov=ai_news_collector_lib -v
```

## Git 工作流

### 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 提交代码

```bash
# 查看变化
git status

# 暂存变化
git add .

# 提交
git commit -m "feat: add your feature description"
# 其他提交类型: fix:, docs:, test:, style:, refactor:, perf:, chore:
```

### 推送分支

```bash
git push origin feature/your-feature-name
```

### 拉取请求

在 GitHub 上创建 PR，提供：
- 清晰的标题
- 详细的描述
- 关联的 Issue（如果有）

### 同步主分支

```bash
git fetch origin
git rebase origin/master
git push origin feature/your-feature-name -f
```

## 调试

### 运行带调试信息的测试

```bash
# 显示 print 输出
pytest -s

# 详细的跟踪信息
pytest --tb=long

# 在失败时进入 debugger
pytest --pdb
```

### 使用 logging 调试

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

## 文档

### 查看项目文档

```bash
# 运行本地服务器查看文档（如果配置了）
# python -m http.server --directory docs 8000
```

### 生成文档

```bash
# 使用 Sphinx 生成文档（如果配置了）
# cd docs && make html
```

## 发布流程

### 本地测试打包

```bash
# 安装构建工具
pip install build twine

# 构建包
python -m build

# 检查包内容
tar -tzf dist/ai-news-collector-lib-0.1.2.tar.gz

# 检查包元数据
twine check dist/*
```

### 上传到 PyPI

```bash
# 设置 PyPI token
export TWINE_PASSWORD="<your-pypi-token>"

# 上传到 TestPyPI（推荐先测试）
python -m twine upload --repository testpypi dist/*

# 上传到 PyPI
python -m twine upload dist/*

# 或使用专用脚本
python upload_to_pypi.py
```

### 创建发布标签

```bash
# 创建标签
git tag -a v0.1.2 -m "Release v0.1.2"

# 推送标签
git push origin v0.1.2

# 或推送所有标签
git push origin --tags
```

## 常用快捷命令

### 一键检查并测试

```bash
# 格式化 + 检查 + 测试
black ai_news_collector_lib/ && flake8 ai_news_collector_lib/ && pytest -v
```

### 快速测试

```bash
# 快速单元测试（无集成测试）
pytest -m "not integration" -q
```

### 清理构建文件

```bash
# 删除 __pycache__ 和 .pyc
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 删除构建和分布文件
rm -rf build/ dist/ *.egg-info/

# 更彻底的清理
git clean -fdx
```

## Windows 特定命令

### PowerShell

```powershell
# 激活虚拟环境
venv\Scripts\Activate.ps1

# 设置环境变量
$env:ALLOW_NETWORK=1

# 运行命令
python -m pytest -v
```

### Git Bash

```bash
# 激活虚拟环境
source venv/Scripts/activate

# 设置环境变量
export ALLOW_NETWORK=1

# 运行命令
python -m pytest -v
```

## 常见问题解决

### ImportError: No module named

```bash
# 重新安装开发依赖
pip install -e ".[dev]" --upgrade --force-reinstall
```

### pytest 找不到测试

```bash
# 确保在项目根目录
cd f:\AI\src\ai_news_collector_lib

# 运行完整路径的 pytest
python -m pytest tests/ -v
```

### 虚拟环境损坏

```bash
# 删除虚拟环境
rm -rf venv

# 重新创建
python -m venv venv
source venv/Scripts/activate  # 或 venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## CI/CD 相关命令

### 本地模拟 CI

```bash
# 模拟 GitHub Actions 的测试
ALLOW_NETWORK=0 python -m pytest -q

# 运行离线集成测试（使用 VCR 磁带）
python -m pytest tests/test_integration_basic.py -v
python -m pytest tests/test_integration_advanced.py -v
```

### 检查构建

```bash
# 验证所有必需文件都在版本控制中
git status

# 检查包的依赖
python setup.py check
```
