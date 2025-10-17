# AI News Collector Library 使用指南

## 📚 目录结构

```
ai_news_collector_lib/
├── __init__.py                 # 库入口
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── collector.py           # 基础搜集器
│   └── advanced_collector.py  # 高级搜集器
├── models/                     # 数据模型
│   ├── __init__.py
│   ├── article.py             # 文章模型
│   └── result.py              # 结果模型
├── config/                     # 配置模块
│   ├── __init__.py
│   └── settings.py            # 配置设置
├── tools/                      # 搜索工具
│   ├── __init__.py
│   └── search_tools.py        # 搜索工具实现
├── utils/                      # 工具模块
│   ├── __init__.py
│   ├── content_extractor.py   # 内容提取器
│   ├── keyword_extractor.py   # 关键词提取器
│   ├── cache.py               # 缓存管理器
│   ├── scheduler.py           # 定时调度器
│   └── reporter.py            # 报告生成器
├── examples/                   # 示例代码
│   ├── basic_usage.py         # 基础使用示例
│   └── advanced_usage.py      # 高级使用示例
├── tests/                      # 测试代码
│   ├── __init__.py
│   └── test_collector.py      # 搜集器测试
├── setup.py                   # 安装脚本
├── requirements.txt           # 依赖列表
├── README.md                  # 项目说明
├── LICENSE                    # 许可证
└── pyproject.toml             # 项目配置
```

## 🚀 快速开始

### 1. 安装库

```bash
# 基础安装
pip install ai-news-collector-lib

# 高级功能安装
pip install ai-news-collector-lib[advanced]

# 开发安装
git clone https://github.com/ai-news-collector/ai-news-collector-lib.git
cd ai-news-collector-lib
pip install -e .
```

### 2. 基础使用

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

### 3. 高级使用

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

## 🔧 配置详解

### 基础配置 (SearchConfig)

```python
from ai_news_collector_lib import SearchConfig

config = SearchConfig(
    # 传统源
    enable_hackernews=True,      # HackerNews
    enable_arxiv=True,           # ArXiv学术论文
    enable_newsapi=False,        # NewsAPI (需要API密钥)
    enable_rss_feeds=True,       # RSS订阅源
    
    # 搜索引擎源
    enable_duckduckgo=True,      # DuckDuckGo搜索
    enable_tavily=False,         # Tavily API (需要API密钥)
    enable_google_search=False,  # Google搜索 (需要API密钥)
    enable_bing_search=False,    # Bing搜索 (需要API密钥)
    enable_serper=False,         # Serper API (需要API密钥)
    enable_brave_search=False,   # Brave搜索 (需要API密钥)
    
    # 搜索参数
    max_articles_per_source=10,  # 每个源最大文章数
    days_back=7,                 # 搜索天数
    similarity_threshold=0.85    # 去重相似度阈值
)
```

### 高级配置 (AdvancedSearchConfig)

```python
from ai_news_collector_lib import AdvancedSearchConfig

config = AdvancedSearchConfig(
    # 继承基础配置
    enable_hackernews=True,
    enable_arxiv=True,
    enable_duckduckgo=True,
    
    # 高级功能
    enable_content_extraction=True,    # 内容提取
    enable_sentiment_analysis=False,  # 情感分析
    enable_keyword_extraction=True,   # 关键词提取
    cache_results=True,                # 结果缓存
    cache_duration_hours=24,          # 缓存时长(小时)
    
    # 内容处理参数
    max_content_length=5000,          # 最大内容长度
    keyword_count=10                  # 关键词数量
)
```

## 📊 支持的搜索源

### 免费源（无需API密钥）

| 源 | 描述 | 特点 |
|---|---|---|
| 🔥 HackerNews | 技术社区讨论 | 高质量技术内容 |
| 📚 ArXiv | 学术论文和预印本 | 最新研究成果 |
| 🦆 DuckDuckGo | 隐私保护的网页搜索 | 无追踪搜索 |

> 注：ArXiv 日期解析与回退
- 优先使用 `BeautifulSoup` 解析 `published`；若 XML 解析失败则回退到 `feedparser`。
- 在 `feedparser` 分支中，日期字段可能仅提供其一：`published_parsed` 或 `updated_parsed`（均为 `time.struct_time`）。
- 回退顺序：`published_parsed` → `updated_parsed` → `datetime.now()`，以最大程度贴近真实发布时间。
- `struct_time` 转换示例：`datetime(*entry.published_parsed[:6])`。

### 付费源（需要API密钥）

| 源 | 描述 | API密钥 | 特点 |
|---|---|---|---|
| 📡 NewsAPI | 多源新闻聚合 | NEWS_API_KEY | 丰富的新闻源 |
| 🔍 Tavily | AI驱动的搜索API | TAVILY_API_KEY | 智能搜索 |
| 🌐 Google Search | Google自定义搜索API | GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_ENGINE_ID | 高质量搜索结果 |
| 🔵 Bing Search | 微软Bing搜索API | BING_SEARCH_API_KEY | 微软搜索技术 |
| ⚡ Serper | 快速Google搜索API | SERPER_API_KEY | 快速Google结果 |
| 🦁 Brave Search | 独立隐私搜索API | BRAVE_SEARCH_API_KEY | 独立搜索索引 |

## 🛠️ 高级功能

### 1. 定时任务

```python
from ai_news_collector_lib import DailyScheduler

# 定义收集函数
async def collect_news_task():
    config = AdvancedSearchConfig(enable_hackernews=True, enable_arxiv=True)
    collector = AdvancedAINewsCollector(config)
    result = await collector.collect_news_advanced("AI news")
    print(f"收集完成: {result['unique_articles']} 篇文章")
    return result

# 创建调度器
scheduler = DailyScheduler(
    collector_func=collect_news_task,
    schedule_time="09:00",
    timezone="Asia/Shanghai"
)

# 启动调度器
scheduler.start()
```

### 2. 缓存管理

```python
from ai_news_collector_lib import CacheManager

# 创建缓存管理器
cache = CacheManager(cache_dir="./cache", default_ttl_hours=24)

# 生成缓存键
cache_key = cache.get_cache_key("artificial intelligence", ["hackernews", "arxiv"])

# 检查缓存
cached_result = cache.get_cached_result(cache_key)
if cached_result:
    print("使用缓存结果")
else:
    # 执行搜索并缓存结果
    result = await collector.collect_news("artificial intelligence")
    cache.cache_result(cache_key, result)

# 获取缓存信息
cache_info = cache.get_cache_info()
print(f"缓存文件数: {cache_info['total_files']}")
print(f"缓存大小: {cache_info['total_size_mb']} MB")
```

### 3. 报告生成

```python
from ai_news_collector_lib import ReportGenerator

# 创建报告生成器
reporter = ReportGenerator(output_dir="./reports")

# 生成Markdown报告
markdown_report = reporter.generate_daily_report(result, format="markdown")
print(markdown_report)

# 生成HTML报告
html_report = reporter.generate_daily_report(result, format="html")

# 保存报告到文件
markdown_file = reporter.save_report(result, format="markdown")
html_file = reporter.save_report(result, format="html")

print(f"Markdown报告: {markdown_file}")
print(f"HTML报告: {html_file}")
```

### 4. 多主题收集

```python
# 收集多个主题
topics = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural networks",
    "computer vision"
]

result = await collector.collect_multiple_topics(topics)

print(f"主题数: {len(result['topics_searched'])}")
print(f"总文章数: {result['total_articles']}")
print(f"独特文章数: {result['unique_articles']}")
print(f"总字数: {result['total_words']:,}")
print(f"平均阅读时间: {result['average_reading_time']} 分钟")

# 显示各主题统计
for topic, stats in result['topic_results'].items():
    if 'error' in stats:
        print(f"❌ {topic}: {stats['error']}")
    else:
        print(f"✅ {topic}: {stats['unique']} 篇独特文章")
```

## 🔌 集成示例

### 1. 作为独立服务

```python
# 在你的项目中
from ai_news_collector_lib import AINewsCollector, SearchConfig

class YourProjectService:
    def __init__(self):
        self.news_collector = AINewsCollector(SearchConfig())
    
    async def get_ai_news(self):
        result = await self.news_collector.collect_news("AI news")
        return result.articles
```

### 2. 作为定时任务

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ai_news_collector_lib import AdvancedAINewsCollector, AdvancedSearchConfig

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=9, minute=0)
async def daily_news_job():
    config = AdvancedSearchConfig(enable_hackernews=True, enable_arxiv=True)
    collector = AdvancedAINewsCollector(config)
    result = await collector.collect_news_advanced("AI")
    # 处理结果...

scheduler.start()
```

### 3. 作为API端点

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

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_collector.py

# 运行异步测试
pytest -v

# 运行带标记的测试
pytest -m "not slow"
```

### 编写测试

```python
import pytest
from ai_news_collector_lib import AINewsCollector, SearchConfig

@pytest.mark.asyncio
async def test_collect_news():
    config = SearchConfig(enable_hackernews=True)
    collector = AINewsCollector(config)
    
    result = await collector.collect_news("test query")
    assert result.total_articles >= 0
    assert result.unique_articles >= 0
```

## 📈 性能优化

### 1. 并发控制

```python
# 限制并发数
import asyncio
from asyncio import Semaphore

class LimitedCollector:
    def __init__(self, max_concurrent=5):
        self.semaphore = Semaphore(max_concurrent)
    
    async def search_with_limit(self, source, query):
        async with self.semaphore:
            return await self._search_source(source, query)
```

### 2. 缓存策略

```python
# 使用Redis缓存
import redis
import json

class RedisCache:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
    
    def get_cached_result(self, key):
        cached = self.redis.get(key)
        return json.loads(cached) if cached else None
    
    def cache_result(self, key, result, ttl=3600):
        self.redis.setex(key, ttl, json.dumps(result))
```

### 3. 错误处理

```python
# 重试机制
import asyncio
from functools import wraps

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    await asyncio.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

@retry(max_attempts=3)
async def search_with_retry(self, source, query):
    return await self._search_source(source, query)
```

## 🚀 部署

### 1. Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "examples/daily_collector.py"]
```

### 2. 环境变量

```bash
# .env文件
NEWS_API_KEY=your_newsapi_key
TAVILY_API_KEY=your_tavily_key
GOOGLE_SEARCH_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id
BING_SEARCH_API_KEY=your_bing_key
SERPER_API_KEY=your_serper_key
BRAVE_SEARCH_API_KEY=your_brave_key
```

### 3. 生产环境配置

```python
# 生产环境配置
config = AdvancedSearchConfig(
    enable_hackernews=True,
    enable_arxiv=True,
    enable_duckduckgo=True,
    enable_content_extraction=True,
    enable_keyword_extraction=True,
    cache_results=True,
    cache_duration_hours=24,
    max_articles_per_source=20
)
```

## 📞 支持

- [问题报告](https://github.com/ai-news-collector/ai-news-collector-lib/issues)
- [讨论区](https://github.com/ai-news-collector/ai-news-collector-lib/discussions)
- [邮件支持](mailto:support@ai-news-collector.com)

---

**祝你使用愉快！** 🎉
