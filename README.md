# AI News Collector Library

一个用于收集AI相关新闻的Python库，支持多种搜索源和高级功能。

## 🚀 特性

- **多源搜索**: 支持HackerNews、ArXiv、DuckDuckGo、NewsAPI等
- **内容提取**: 自动提取网页内容
- **关键词分析**: 智能提取关键词
- **结果缓存**: 支持结果缓存，提高效率
- **定时任务**: 支持定时自动收集
- **报告生成**: 生成多种格式的报告
- **易于集成**: 简单的API接口

## 📁 项目结构

```
ai_news_collector_lib/
├── __init__.py          # 主模块入口
├── cli.py              # 命令行接口
├── config/             # 配置模块
│   ├── __init__.py
│   ├── settings.py     # 搜索配置
│   └── api_keys.py     # API密钥管理
├── core/               # 核心功能
│   ├── __init__.py
│   ├── collector.py    # 基础收集器
│   └── advanced_collector.py  # 高级收集器
├── models/             # 数据模型
│   ├── __init__.py
│   ├── article.py      # 文章模型
│   └── result.py       # 结果模型
├── tools/              # 搜索工具
│   ├── __init__.py
│   └── search_tools.py # 各种搜索工具
├── utils/              # 工具函数
│   ├── __init__.py
│   ├── cache.py        # 缓存管理
│   ├── content_extractor.py  # 内容提取
│   ├── keyword_extractor.py # 关键词提取
│   ├── reporter.py     # 报告生成
│   └── scheduler.py    # 任务调度
├── tests/              # 测试文件
├── examples/           # 使用示例
├── scripts/            # 构建脚本
├── setup.py           # 安装配置
├── pyproject.toml     # 项目配置
└── README.md          # 项目说明
```

## 📦 安装

### 基础安装

```bash
pip install ai-news-collector-lib
```

### 高级功能安装

```bash
pip install ai-news-collector-lib[advanced]
```

### 开发安装

```bash
git clone https://github.com/ai-news-collector/ai-news-collector-lib.git
cd ai-news-collector-lib
pip install -e .
```

## 🔧 快速开始

### 基础使用

```python
import asyncio
from ai_news_collector_lib import AINewsCollector, SearchConfig

# 创建配置
config = SearchConfig(
    enable_hackernews=True,
    enable_arxiv=True,
    enable_duckduckgo=True,
    max_articles_per_source=10
)

# 创建搜集器
collector = AINewsCollector(config)

# 收集新闻
async def main():
    result = await collector.collect_news("artificial intelligence")
    print(f"收集到 {result.total_articles} 篇文章")
    return result.articles

# 运行
articles = asyncio.run(main())
```

### 高级使用

```python
from ai_news_collector_lib import AdvancedAINewsCollector, AdvancedSearchConfig

# 创建高级配置
config = AdvancedSearchConfig(
    enable_hackernews=True,
    enable_arxiv=True,
    enable_duckduckgo=True,
    enable_content_extraction=True,
    enable_keyword_extraction=True,
    cache_results=True
)

# 创建高级搜集器
collector = AdvancedAINewsCollector(config)

# 收集增强新闻
async def main():
    result = await collector.collect_news_advanced("machine learning")
    
    # 分析结果
    total_words = sum(article['word_count'] for article in result['articles'])
    print(f"总字数: {total_words}")
    
    return result

# 运行
enhanced_result = asyncio.run(main())
```

## 📊 支持的搜索源

### 免费源

- 🔥 **HackerNews** - 技术社区讨论
- 📚 **ArXiv** - 学术论文和预印本
- 🦆 **DuckDuckGo** - 隐私保护的网页搜索

### 付费源 (需要API密钥)

- 📡 **NewsAPI** - 多源新闻聚合
- 🔍 **Tavily** - AI驱动的搜索API
- 🌐 **Google Search** - Google自定义搜索API
- 🔵 **Bing Search** - 微软Bing搜索API
- ⚡ **Serper** - 快速Google搜索API
- 🦁 **Brave Search** - 独立隐私搜索API
- 🔬 **MetaSota Search** - 基于MCP协议的智能搜索服务

## ⚙️ 配置

### 环境变量

```bash
# API密钥
NEWS_API_KEY=your_newsapi_key
TAVILY_API_KEY=your_tavily_key
GOOGLE_SEARCH_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id
BING_SEARCH_API_KEY=your_bing_key
SERPER_API_KEY=your_serper_key
BRAVE_SEARCH_API_KEY=your_brave_key
METASOSEARCH_API_KEY=your_metasota_key
```

### 配置文件

```python
from ai_news_collector_lib import SearchConfig

config = SearchConfig(
    # 传统源
    enable_hackernews=True,
    enable_arxiv=True,
    enable_newsapi=False,
    enable_rss_feeds=True,
    
    # 搜索引擎源
    enable_duckduckgo=True,
    enable_tavily=False,
    enable_google_search=False,
    enable_bing_search=False,
    enable_serper=False,
    enable_brave_search=False,
    enable_metasota_search=False,
    
    # 搜索参数
    max_articles_per_source=10,
    days_back=7,
    similarity_threshold=0.85
)
```

## 🛠️ 高级功能

### 定时任务

```python
from ai_news_collector_lib import DailyScheduler

# 创建调度器
scheduler = DailyScheduler(
    collector_func=collect_news,
    schedule_time="09:00",
    timezone="Asia/Shanghai"
)

# 启动调度器
scheduler.start()
```

### 缓存管理

```python
from ai_news_collector_lib import CacheManager

# 创建缓存管理器
cache = CacheManager(cache_dir="./cache", default_ttl_hours=24)

# 检查缓存
cache_key = cache.get_cache_key("ai news", ["hackernews", "arxiv"])
cached_result = cache.get_cached_result(cache_key)

if cached_result:
    print("使用缓存结果")
else:
    # 执行搜索并缓存结果
    result = await collector.collect_news("ai news")
    cache.cache_result(cache_key, result)
```

### 报告生成

```python
from ai_news_collector_lib import ReportGenerator

# 创建报告生成器
reporter = ReportGenerator(output_dir="./reports")

# 生成报告
report = reporter.generate_daily_report(result, format="markdown")
reporter.save_report(result, filename="daily_report.md")
```

## 📈 使用示例

### 每日收集脚本

```python
#!/usr/bin/env python3
import asyncio
from ai_news_collector_lib import AdvancedAINewsCollector, AdvancedSearchConfig

async def daily_collection():
    # 配置
    config = AdvancedSearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        enable_duckduckgo=True,
        enable_content_extraction=True,
        cache_results=True
    )
    
    # 创建搜集器
    collector = AdvancedAINewsCollector(config)
    
    # 收集多个主题
    topics = ["artificial intelligence", "machine learning", "deep learning"]
    result = await collector.collect_multiple_topics(topics)
    
    print(f"收集完成: {result['unique_articles']} 篇独特文章")
    return result

if __name__ == "__main__":
    asyncio.run(daily_collection())
```

### Web API集成

```python
from fastapi import FastAPI
from ai_news_collector_lib import AINewsCollector, SearchConfig

app = FastAPI()
collector = AINewsCollector(SearchConfig())

@app.get("/ai-news")
async def get_ai_news(query: str = "artificial intelligence"):
    result = await collector.collect_news(query)
    return {
        "total": result.total_articles,
        "unique": result.unique_articles,
        "articles": [article.to_dict() for article in result.articles]
    }
```

## 🧪 测试

```bash
# 运行测试
pytest

# 运行异步测试
pytest -v

# 运行特定测试
pytest tests/test_collector.py
```

## 🗓️ ArXiv 日期解析与回退

- 默认采用 `BeautifulSoup` 的 XML 解析获取 `published` 字段；若解析异常则回退到 `feedparser`。
- 在 `feedparser` 分支中，日期字段可能仅存在其一：`published_parsed` 或 `updated_parsed`，两者类型均为 `time.struct_time`。
- 回退顺序为：`published_parsed` → `updated_parsed` → `datetime.now()`，以尽量保持条目的时间接近真实发布时间。
- 将 `struct_time` 转换为 `datetime` 时仅取到秒位：`datetime(*entry.published_parsed[:6])` 或 `datetime(*entry.updated_parsed[:6])`。
- 时区说明：Atom 中尾部 `Z` 表示 UTC。BS4 分支使用 `published_str.replace('Z', '+00:00')` 后通过 `datetime.fromisoformat` 解析；`feedparser` 分支直接由 `struct_time` 构建 `datetime`。

实现节选（位于 `ai_news_collector_lib/tools/search_tools.py` 的 `ArxivTool`）：

```python
feed = feedparser.parse(response.content)
for entry in feed.entries:
    # 说明：feedparser 可能仅提供 published_parsed 或 updated_parsed
    # 回退顺序：published_parsed > updated_parsed > 当前时间
    try:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            published_date = datetime(*entry.updated_parsed[:6])
        else:
            published_date = datetime.now()
    except Exception:
        published_date = datetime.now()
```

最小验证脚本：`scripts/min_check_feedparser_fallback.py`

```bash
python scripts/min_check_feedparser_fallback.py
```

该脚本分别构造 RSS (`pubDate`) 与 Atom (`updated`) 的示例，在仅存在其中一个日期字段时验证回退逻辑能够正常运行且不抛异常。

## 📚 文档

- [完整文档](https://ai-news-collector-lib.readthedocs.io/)
- [API参考](https://ai-news-collector-lib.readthedocs.io/api/)
- [示例代码](https://github.com/ai-news-collector/ai-news-collector-lib/tree/main/examples)

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

本项目采用 MIT 许可证。查看 [LICENSE](LICENSE) 文件了解详细信息。

## 🆘 支持

- [问题报告](https://github.com/ai-news-collector/ai-news-collector-lib/issues)
- [讨论区](https://github.com/ai-news-collector/ai-news-collector-lib/discussions)
- [邮件支持](mailto:support@ai-news-collector.com)

## 🔄 更新日志

### v0.1.0 (2025-10-07)

- 初始预发布版本
- 支持基础搜索功能
- 支持多种搜索源
- 支持高级功能（内容提取、关键词分析、缓存等）
- ⚠️ 注意：这是预发布版本，功能可能不稳定

---

**祝你使用愉快！** 🎉
