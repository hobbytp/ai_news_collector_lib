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
