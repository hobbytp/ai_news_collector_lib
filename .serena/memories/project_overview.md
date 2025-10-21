# AI News Collector Library - 项目概览

## 项目基本信息

**项目名称**: AI News Collector Library (`ai-news-collector-lib`)  
**版本**: 0.1.2  
**许可证**: MIT  
**开发语言**: Python  
**支持版本**: Python 3.8+  
**现在日期**: 2025年10月19日

## 项目目标与功能

AI News Collector Library 是一个 Python 库，用于从多个来源收集 AI 相关新闻。

### 核心功能

1. **多源新闻搜索**
   - HackerNews（免费）
   - ArXiv（免费）
   - DuckDuckGo（免费）
   - NewsAPI、Tavily、Google Search、Bing Search、Serper、Brave Search（需要 API 密钥）

2. **内容增强**
   - 网页内容提取
   - 关键词分析
   - 结果去重

3. **数据管理**
   - 结果缓存
   - 定时任务调度
   - 报告生成

4. **易用性**
   - 简单的同步/异步 API
   - 灵活的配置系统
   - 命令行工具

## 项目架构

### 核心模块

| 模块 | 路径 | 功能 |
|------|------|------|
| **Core** | `ai_news_collector_lib/core/` | 基础和高级搜集器 |
| **Models** | `ai_news_collector_lib/models/` | Article、SearchResult 数据模型 |
| **Config** | `ai_news_collector_lib/config/` | 搜索配置管理 |
| **Tools** | `ai_news_collector_lib/tools/` | 各种搜索源的实现 |
| **Utils** | `ai_news_collector_lib/utils/` | 工具函数（缓存、提取、调度、报告） |
| **CLI** | `ai_news_collector_lib/cli.py` | 命令行接口 |

### 数据流

用户请求 → 配置加载 → 搜集器初始化 → 并行搜索 → 结果收集 → 去重 → 内容提取 → 关键词分析 → 缓存 → 返回结果

### 关键类

- `AINewsCollector`: 基础搜集器
- `AdvancedAINewsCollector`: 高级搜集器（包含内容提取、关键词分析）
- `Article`: 基础文章数据结构
- `AdvancedArticle`: 增强文章数据结构（含关键词、情感、阅读时间）
- `SearchConfig`: 基础搜索配置
- `AdvancedSearchConfig`: 高级搜索配置

## 项目结构

```
ai_news_collector_lib/
├── __init__.py                 # 导出主要接口
├── cli.py                      # 命令行工具
├── core/                       # 核心搜集器
│   ├── collector.py           # 基础搜集器
│   └── advanced_collector.py  # 高级搜集器
├── models/                     # 数据模型
│   ├── article.py             # Article、AdvancedArticle
│   └── result.py              # SearchResult
├── config/                     # 配置
│   └── settings.py            # SearchConfig、AdvancedSearchConfig
├── tools/                      # 搜索工具
│   └── search_tools.py        # 各种搜索源实现
├── utils/                      # 工具函数
│   ├── cache.py               # 缓存管理
│   ├── content_extractor.py   # 内容提取
│   ├── keyword_extractor.py   # 关键词提取
│   ├── reporter.py            # 报告生成
│   ├── scheduler.py           # 定时调度
├── examples/                   # 示例代码
├── tests/                      # 单元测试
└── docs/                       # 文档
```

## 项目特点

### 设计原则

1. **模块化**: 每个模块只负责一个功能
2. **可扩展**: 易于添加新的搜索源
3. **异步优先**: 支持并发搜索
4. **容错性强**: 单个源失败不影响整体

### 代码质量

- 使用 Python 3.8+ 类型提示
- 采用 dataclass 进行数据建模
- 完整的文档字符串（docstring）
- 全面的单元和集成测试覆盖

## 关键依赖

### 必需依赖
- requests >= 2.28.0 (HTTP 请求)
- beautifulsoup4 >= 4.11.0 (HTML 解析)
- feedparser >= 6.0.0 (RSS 解析)
- python-dotenv >= 0.19.0 (环境变量管理)

### 可选依赖
- **advanced**: aiohttp、redis、schedule、apscheduler (异步、缓存、调度)
- **nlp**: nltk、spacy、textblob (NLP 处理)
- **web**: fastapi、uvicorn、streamlit (Web 框架)
- **dev**: pytest、pytest-asyncio、black、flake8、mypy、vcrpy (开发工具)

## 部署信息

**构建系统**: setuptools  
**打包工具**: setuptools_scm  
**包管理**: PyPI（https://pypi.org/project/ai-news-collector-lib/）

### 命令行入口点

```
ai-news-collector -> ai_news_collector_lib.cli:main
```

## 示例用法

### 基础使用
```python
from ai_news_collector_lib import AINewsCollector, SearchConfig

config = SearchConfig(enable_hackernews=True, enable_arxiv=True)
collector = AINewsCollector(config)
result = await collector.collect_news("artificial intelligence")
```

### 高级使用
```python
from ai_news_collector_lib import AdvancedAINewsCollector, AdvancedSearchConfig

config = AdvancedSearchConfig(
    enable_hackernews=True,
    enable_content_extraction=True,
    enable_keyword_extraction=True,
    cache_results=True
)
collector = AdvancedAINewsCollector(config)
result = await collector.collect_news_advanced("machine learning")
```
