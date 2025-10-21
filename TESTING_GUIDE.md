# 测试指南

## 运行测试

### 1. 激活conda环境（如果使用conda）

```bash
conda activate news_collector
```

### 2. 安装测试依赖

```bash
# 安装基础依赖
pip install -e ".[dev]"

# 安装高级依赖（包含schedule等模块）
pip install -e ".[advanced]"
```

### 3. 运行测试

```bash
# 运行所有测试
python -m pytest -v

# 运行特定测试文件
python -m pytest tests/test_collector.py -v

# 运行特定测试方法
python -m pytest tests/test_collector.py::TestAINewsCollector::test_initialization -v

# 运行测试并显示覆盖率
python -m pytest --cov=ai_news_collector_lib -v
```

### 4. 运行不同类型的测试

```bash
# 只运行单元测试（快速，使用mock）
python -m pytest -m "not integration" -v

# 只运行集成测试（需要真实API密钥）
python -m pytest -m "integration" -v

# 跳过慢速测试
python -m pytest -m "not slow" -v

# 运行所有测试（包括集成测试）
python -m pytest -v
```

## 环境变量设置

### 方式1：使用.env文件（推荐）

在项目根目录创建`.env`文件：

```bash
# AI News Collector Library - 环境变量配置
# NewsAPI (https://newsapi.org/)
NEWS_API_KEY=your_newsapi_key_here

# Tavily Search (https://tavily.com/)
TAVILY_API_KEY=your_tavily_api_key_here

# Google Custom Search (https://developers.google.com/custom-search/)
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_google_search_engine_id_here

# Bing Search API (https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)
BING_SEARCH_API_KEY=your_bing_search_api_key_here

# Serper API (https://serper.dev/)
SERPER_API_KEY=your_serper_api_key_here

# Brave Search API (https://brave.com/search/api/)
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here

# MetaSota Search (https://metaso.cn/) - MCP协议搜索服务
METASOSEARCH_API_KEY=your_metasota_search_api_key_here
```

### 方式2：使用export命令

在Windows (Git Bash)中：

```bash
export NEWS_API_KEY="your_newsapi_key_here"
export TAVILY_API_KEY="your_tavily_api_key_here"
export GOOGLE_SEARCH_API_KEY="your_google_search_api_key_here"
export GOOGLE_SEARCH_ENGINE_ID="your_google_search_engine_id_here"
export BING_SEARCH_API_KEY="your_bing_search_api_key_here"
export SERPER_API_KEY="your_serper_api_key_here"
export BRAVE_SEARCH_API_KEY="your_brave_search_api_key_here"
export METASOSEARCH_API_KEY="your_metasota_search_api_key_here"
```

在Windows PowerShell中：

```powershell
$env:NEWS_API_KEY="your_newsapi_key_here"
$env:TAVILY_API_KEY="your_tavily_api_key_here"
$env:GOOGLE_SEARCH_API_KEY="your_google_search_api_key_here"
$env:GOOGLE_SEARCH_ENGINE_ID="your_google_search_engine_id_here"
$env:BING_SEARCH_API_KEY="your_bing_search_api_key_here"
$env:SERPER_API_KEY="your_serper_api_key_here"
$env:BRAVE_SEARCH_API_KEY="your_brave_search_api_key_here"
$env:METASOSEARCH_API_KEY="your_metasota_search_api_key_here"
```

### 方式3：在测试中直接设置

```python
import os
os.environ["NEWS_API_KEY"] = "your_newsapi_key_here"
os.environ["TAVILY_API_KEY"] = "your_tavily_api_key_here"
os.environ["METASOSEARCH_API_KEY"] = "your_metasota_search_api_key_here"
```

## 测试配置

项目已经配置了pytest，支持：

- 异步测试 (`pytest-asyncio`)
- 测试标记 (`@pytest.mark.asyncio`)
- 详细输出 (`-v`)
- 短错误追踪 (`--tb=short`)

## 测试标记

- `@pytest.mark.slow`: 标记为慢速测试
- `@pytest.mark.integration`: 标记为集成测试
- `@pytest.mark.unit`: 标记为单位测试

## 运行特定类型的测试

```bash
# 只运行单位测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"

# 只运行集成测试
pytest -m integration
```

## 集成测试

### 什么是集成测试？

集成测试使用真实的API密钥来测试完整的功能，包括：

- 验证API密钥是否正确配置
- 测试真实的API调用
- 验证数据收集和处理流程
- 测试错误处理和边界情况

### 运行集成测试

```bash
# 运行所有集成测试
python -m pytest tests/test_integration.py -v

# 运行特定的集成测试
python -m pytest tests/test_integration.py::TestIntegration::test_real_news_collection -v

# 运行API密钥验证测试
python -m pytest tests/test_integration.py::TestIntegration::test_api_keys_validation -v
```

### 集成测试特点

- **需要真实API密钥**：确保在`.env`文件中配置了相应的API密钥
- **会产生API调用费用**：某些API服务可能收费
- **运行时间较长**：因为需要等待真实的API响应
- **标记为`@pytest.mark.integration`**：可以单独运行或跳过

### 集成测试用例

#### 基础集成测试

1. **API密钥验证**：检查配置的API密钥是否有效
2. **真实新闻收集**：使用真实API收集新闻
3. **特定源测试**：测试单个搜索源的功能
4. **错误处理测试**：测试API错误处理
5. **配置验证**：验证搜索配置
6. **综合测试**：完整的功能测试（标记为慢速）

#### 高级集成测试

1. **高级配置验证**：验证高级搜索配置
2. **高级新闻收集**：测试高级收集器的完整功能
3. **内容提取测试**：验证文章内容提取功能
4. **关键词提取测试**：验证关键词分析功能
5. **缓存功能测试**：验证结果缓存机制
6. **高级错误处理**：测试高级功能的错误处理
7. **综合高级测试**：完整的高级功能测试（标记为慢速）

## 注意事项

1. `.env`文件应该添加到`.gitignore`中，不要提交到版本控制
2. 单元测试使用mock，不需要真实的API密钥
3. 集成测试需要真实的API密钥，会产生API调用费用
4. 项目已经配置了`python-dotenv`来自动加载`.env`文件
5. 集成测试标记为`@pytest.mark.integration`，可以单独运行

## VCR 录制/回放（稳定网络集成测试）

项目已集成 [vcrpy]，支持将网络请求“录制”为磁带（YAML），之后回放以避免网络抖动：

- 磁带目录：`tests/cassettes/`
- 环境变量：
  - `ALLOW_NETWORK=1` 允许触网（首次运行会录制磁带）
  - `UPDATE_CASSETTES=1` 强制重新录制磁带（与 `ALLOW_NETWORK=1` 搭配）

### 使用方法

```bash
# 首次录制（允许网络，若磁带不存在则录制；存在则回放）
ALLOW_NETWORK=1 python -m pytest -m network -v

# 更新（重新录制所有相关磁带）
UPDATE_CASSETTES=1 ALLOW_NETWORK=1 python -m pytest -m network -v

# 离线回放（不触网，仅回放已有磁带；如无磁带则跳过或失败）
python -m pytest -m network -v
```

> ⚠️ 注意：当前测试代码如果在 `ALLOW_NETWORK != 1` 时无条件跳过网络测试，则不会自动回放已有磁带。要实现真正的离线回放，需确保测试只在"磁带缺失"时才跳过，否则应调整 skip 条件或参考测试代码实现。

> 提示：我们的网络集成测试在 `tests/test_integration_basic.py` 与 `tests/test_integration_advanced.py` 已使用磁带。
> 离线单元测试（如 ArXiv 回退逻辑）不需要磁带。

## CI 测试与发布流程

- Push/PR 测试工作流：`.github/workflows/test.yml`
  - Python `3.12`，安装 `.[dev]` 依赖（包含 `vcrpy`）。
  - 以离线模式运行测试：`ALLOW_NETWORK=0 python -m pytest -q`（使用已提交的磁带回放）。

- 发布工作流：`.github/workflows/publish.yml`
  - 发布前安装构建工具与 `.[dev]` 依赖。
  - 运行离线测试（VCR 回放）后再执行打包与发布：`python -m build` + `twine upload`。
  - 使用 GitHub Secrets `PYPI_API_TOKEN` 执行发布。

### 本地录制/回放与发布的推荐流程

```bash
# 1) 安装开发依赖（确保有 vcrpy 和 pytest）
pip install -e .[dev]

# 2) 离线回放（默认）
python -m pytest -m network -v

# 3) 首次录制或更新磁带
ALLOW_NETWORK=1 python -m pytest -m network -v
ALLOW_NETWORK=1 UPDATE_CASSETTES=1 python -m pytest -m network -v

# 4) 本地打包（发布前自检）
python -m build

# 5) 本地上传到 PyPI（需要环境变量 TWINE_PASSWORD 设置为 PyPI Token）
export TWINE_PASSWORD="<your-pypi-token>"  # Windows PowerShell: $env:TWINE_PASSWORD="..."
python -m twine upload dist/*
```

> 注意：`upload_to_pypi.py` 脚本也可用于上传，但需提前设置 `TWINE_PASSWORD`。若你的网络需要代理，可在终端中设置 `HTTPS_PROXY` 环境变量后再执行上传。

## 快速开始

### 1. 运行单元测试（推荐开始）

```bash
conda activate news_collector
python -m pytest -m "not integration" -v
```

### 2. 配置API密钥（可选）

```bash
# 复制示例文件
cp env.example .env

# 编辑.env文件，填入你的API密钥
# 注意：免费源（HackerNews、ArXiv、DuckDuckGo）无需配置
```

### 3. 运行集成测试

```bash
# 验证API密钥配置
python -m pytest tests/test_integration.py::TestIntegration::test_api_keys_validation -v -s

# 测试免费源
python -m pytest tests/test_integration.py::TestIntegration::test_specific_source_collection -v -s

# 运行所有集成测试（需要API密钥）
python -m pytest -m integration -v

# 运行高级集成测试
python -m pytest tests/test_integration.py::TestAdvancedIntegration -v

# 运行特定高级功能测试
python -m pytest tests/test_integration.py::TestAdvancedIntegration::test_advanced_news_collection -v -s
```

### 4. 运行所有测试

```bash
python -m pytest -v
```

## 测试结果示例

### 单元测试结果

```
======================== 12 passed in 0.58s =========================
```

### 集成测试结果

#### 基础集成测试结果

```
测试源: hackernews
hackernews 状态: completed
hackernews 找到 2 篇文章
测试源: arxiv
arxiv 状态: completed
arxiv 找到 0 篇文章
测试源: duckduckgo
duckduckgo 状态: completed
duckduckgo 找到 0 篇文章
PASSED
```

#### 高级集成测试结果

```
开始高级新闻收集测试，查询: 'machine learning'
启用的高级功能: {'content_extraction': True, 'sentiment_analysis': False, 'keyword_extraction': True, 'caching': True}
收集到 4 篇文章
去重后 4 篇
去除了 0 篇重复文章
hackernews: completed - 2 篇
arxiv: completed - 0 篇
duckduckgo: completed - 0 篇
newsapi: completed - 2 篇
PASSED
```

## 付费API测试

### 快速开始

付费API测试使用VCR（视频磁带录制/回放）技术进行离线测试：

1. **首次运行（录制真实API响应）**：
```bash
# 在.env中配置API密钥
export TAVILY_API_KEY="your-key"
export GOOGLE_SEARCH_API_KEY="your-key"
# ... 其他API密钥

# 运行测试（会自动录制cassettes）
python -m pytest tests/test_paid_apis.py -v
```

2. **后续运行（使用录制的cassettes）**：
```bash
# 无需API密钥，直接运行
python -m pytest tests/test_paid_apis.py -v
```

### 支持的付费API

| API | 环境变量 | Cassette文件 |
|-----|---------|------------|
| Tavily Search | `TAVILY_API_KEY` | tavily_search.yaml |
| Google Search | `GOOGLE_SEARCH_API_KEY` + `GOOGLE_SEARCH_ENGINE_ID` | google_search.yaml |
| Serper | `SERPER_API_KEY` | serper_search.yaml |
| Brave Search | `BRAVE_SEARCH_API_KEY` | brave_search.yaml |
| MetaSota | `METASOSEARCH_API_KEY` | metasota_search.yaml |
| NewsAPI | `NEWS_API_KEY` | newsapi_search.yaml |

### 常见问题

**Q: 我没有配置API密钥，测试会怎样？**  
A: 如果没有配置API密钥且没有对应的cassette文件，测试会被跳过。如果有cassette，测试会使用录制的数据离线运行。

**Q: 如何更新cassette（重新录制API响应）？**  
A: 删除对应的cassette文件，配置API密钥，再次运行测试即可重新录制。

**Q: cassette文件是什么？**  
A: cassette是VCR录制的HTTP交互文件（YAML格式），包含了API的请求和响应。这样可以离线测试而不消耗API配额。

### 使用Makefile运行测试

```bash
# 运行所有测试
make test

# 只运行基础测试（快速）
make test-basic

# 只运行付费API测试
make test-paid

# 运行测试并生成覆盖率报告
make test-cov
```

### 详细指南

更多信息请参考：
- [CI/CD GitHub Actions 指南](../docs/CI_CD_GITHUB_ACTIONS_GUIDE.md)
- [付费API测试指南](../docs/PAID_API_TESTING_GUIDE.md)
