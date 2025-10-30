# 灵活API使用示例

本文档展示了如何使用新的灵活API接口，支持单个搜索引擎选择和独立参数设置。

## 🎯 主要特性

- **单个搜索引擎选择**：可以只使用某个特定的搜索引擎
- **独立参数设置**：每个搜索引擎可以设置不同的参数
- **预设时间范围**：支持一天、一周、一个月、一年的预设选项
- **自定义时间范围**：支持自定义天数设置
- **动态配置更新**：可以在运行时更新搜索引擎配置

## 📚 基础使用

### 1. 使用单个搜索引擎

```python
import asyncio
from ai_news_collector_lib import collect_with_single_engine, TimeRange

async def main():
    # 只使用HackerNews搜索，搜索最近一周的新闻
    result = await collect_with_single_engine(
        engine_name="hackernews",
        query="artificial intelligence",
        time_range=TimeRange.ONE_WEEK,
        max_articles=10
    )
    
    print(f"找到 {result.unique_articles} 篇文章")
    for article in result.articles[:3]:
        print(f"- {article.title}")

asyncio.run(main())
```

### 2. 使用多个搜索引擎

```python
import asyncio
from ai_news_collector_lib import collect_with_multiple_engines, TimeRange

async def main():
    # 使用多个搜索引擎，搜索最近一天的新闻
    result = await collect_with_multiple_engines(
        engine_names=["hackernews", "arxiv", "duckduckgo"],
        query="machine learning",
        time_range=TimeRange.ONE_DAY,
        max_articles_per_engine=5
    )
    
    print(f"总共找到 {result.unique_articles} 篇文章")
    print(f"去重前: {result.total_articles} 篇")
    print(f"去重后: {result.unique_articles} 篇")

asyncio.run(main())
```

## ⚙️ 高级配置

### 1. 创建灵活配置

```python
from ai_news_collector_lib import FlexibleSearchConfig, TimeRange, FlexibleAINewsCollector

# 创建配置
config = FlexibleSearchConfig()

# 配置HackerNews：搜索最近一天，最多5篇文章
config.set_engine_config(
    engine_name="hackernews",
    enabled=True,
    max_articles=5,
    time_range=TimeRange.ONE_DAY
)

# 配置ArXiv：搜索最近一个月，最多15篇文章
config.set_engine_config(
    engine_name="arxiv",
    enabled=True,
    max_articles=15,
    time_range=TimeRange.ONE_MONTH
)

# 配置DuckDuckGo：搜索最近一周，最多10篇文章
config.set_engine_config(
    engine_name="duckduckgo",
    enabled=True,
    max_articles=10,
    time_range=TimeRange.ONE_WEEK
)

# 创建收集器
collector = FlexibleAINewsCollector(config)
```

### 2. 使用收集器

```python
import asyncio

async def main():
    # 搜索所有启用的引擎
    result = await collector.collect_news("deep learning")
    
    # 只搜索特定引擎
    result = await collector.collect_news(
        "neural networks", 
        engines=["hackernews", "arxiv"]
    )
    
    print(f"搜索结果: {result.unique_articles} 篇文章")

asyncio.run(main())
```

## 🕒 时间范围设置

### 1. 预设时间范围

```python
from ai_news_collector_lib import TimeRange

# 一天内的新闻
config.set_engine_config("hackernews", time_range=TimeRange.ONE_DAY)

# 一周内的新闻
config.set_engine_config("arxiv", time_range=TimeRange.ONE_WEEK)

# 一个月内的新闻
config.set_engine_config("duckduckgo", time_range=TimeRange.ONE_MONTH)

# 一年内的新闻
config.set_engine_config("newsapi", time_range=TimeRange.ONE_YEAR)
```

### 2. 自定义时间范围

```python
# 自定义搜索最近3天的新闻
config.set_engine_config(
    engine_name="hackernews",
    time_range=TimeRange.CUSTOM,
    custom_days=3
)
```

### 3. 为所有引擎设置统一时间范围

```python
# 所有引擎都搜索最近一周的新闻
config.set_time_range_preset(TimeRange.ONE_WEEK)
```

## 🔧 动态配置更新

### 1. 运行时更新引擎配置

```python
# 启用新的搜索引擎
collector.update_engine_config(
    engine_name="tavily",
    enabled=True,
    api_key="your-api-key",
    max_articles=8,
    time_range=TimeRange.ONE_DAY
)

# 更新现有引擎的时间范围
collector.set_time_range_for_engine("hackernews", TimeRange.ONE_MONTH)

# 为所有引擎设置新的时间范围
collector.set_time_range_for_all_engines(TimeRange.ONE_WEEK)
```

### 2. 查看引擎信息

```python
# 获取可用的搜索引擎
available_engines = collector.get_available_engines()
print(f"可用引擎: {available_engines}")

# 获取引擎详细信息
engine_info = collector.get_engine_info()
for engine_name, info in engine_info.items():
    print(f"{engine_name}: {info['time_range']}, {info['max_articles']} 篇文章")
```

## 💡 实用示例

### 1. 快速搜索最近热点

```python
import asyncio
from ai_news_collector_lib import collect_with_single_engine, TimeRange

async def search_today_hot_news(topic: str):
    """搜索今天的热点新闻"""
    result = await collect_with_single_engine(
        engine_name="hackernews",
        query=topic,
        time_range=TimeRange.ONE_DAY,
        max_articles=20
    )
    
    print(f"今天关于 '{topic}' 的热点新闻:")
    for i, article in enumerate(result.articles, 1):
        print(f"{i}. {article.title}")
        print(f"   来源: {article.source_name}")
        print(f"   时间: {article.published}")
        print()

asyncio.run(search_today_hot_news("AI"))
```

### 2. 学术论文搜索

```python
import asyncio
from ai_news_collector_lib import collect_with_single_engine, TimeRange

async def search_recent_papers(topic: str):
    """搜索最近的学术论文"""
    result = await collect_with_single_engine(
        engine_name="arxiv",
        query=topic,
        time_range=TimeRange.ONE_MONTH,
        max_articles=15
    )
    
    print(f"最近一个月关于 '{topic}' 的论文:")
    for article in result.articles:
        print(f"- {article.title}")
        print(f"  摘要: {article.summary[:100]}...")
        print(f"  链接: {article.url}")
        print()

asyncio.run(search_recent_papers("transformer"))
```

### 3. 多源对比搜索

```python
import asyncio
from ai_news_collector_lib import FlexibleSearchConfig, TimeRange, FlexibleAINewsCollector

async def compare_sources(topic: str):
    """对比不同搜索引擎的结果"""
    config = FlexibleSearchConfig()
    
    # 配置不同引擎使用不同的时间范围
    config.set_engine_config("hackernews", time_range=TimeRange.ONE_DAY, max_articles=5)
    config.set_engine_config("arxiv", time_range=TimeRange.ONE_WEEK, max_articles=5)
    config.set_engine_config("duckduckgo", time_range=TimeRange.ONE_MONTH, max_articles=5)
    
    collector = FlexibleAINewsCollector(config)
    result = await collector.collect_news(topic)
    
    # 按来源分组显示结果
    by_source = {}
    for article in result.articles:
        source = article.source
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(article)
    
    for source, articles in by_source.items():
        print(f"\n=== {source.upper()} ({len(articles)} 篇) ===")
        for article in articles:
            print(f"- {article.title}")

asyncio.run(compare_sources("quantum computing"))
```

### 4. 渐进式搜索

```python
import asyncio
from ai_news_collector_lib import FlexibleSearchConfig, TimeRange, FlexibleAINewsCollector

async def progressive_search(topic: str):
    """渐进式搜索：从最近到更早的时间"""
    config = FlexibleSearchConfig()
    
    # 先搜索最近一天
    config.set_engine_config("hackernews", time_range=TimeRange.ONE_DAY, max_articles=10)
    collector = FlexibleAINewsCollector(config)
    
    print("=== 最近一天的新闻 ===")
    result1 = await collector.collect_news(topic)
    print(f"找到 {result1.unique_articles} 篇文章")
    
    # 如果结果不够，扩展到最近一周
    if result1.unique_articles < 5:
        print("\n=== 扩展到最近一周 ===")
        collector.set_time_range_for_engine("hackernews", TimeRange.ONE_WEEK)
        result2 = await collector.collect_news(topic)
        print(f"找到 {result2.unique_articles} 篇文章")
        
        # 如果还不够，再扩展到最近一个月
        if result2.unique_articles < 10:
            print("\n=== 扩展到最近一个月 ===")
            collector.set_time_range_for_engine("hackernews", TimeRange.ONE_MONTH)
            result3 = await collector.collect_news(topic)
            print(f"找到 {result3.unique_articles} 篇文章")

asyncio.run(progressive_search("blockchain"))
```

## 🔍 支持的搜索引擎

### 免费搜索引擎
- `hackernews` - HackerNews技术社区
- `arxiv` - 学术论文预印本
- `duckduckgo` - 隐私搜索引擎
- `rss_feeds` - RSS订阅源

### 付费搜索引擎（需要API密钥）
- `newsapi` - NewsAPI新闻聚合
- `tavily` - Tavily AI搜索
- `google_search` - Google搜索API
- `bing_search` - Bing搜索API
- `serper` - Serper搜索API
- `brave_search` - Brave搜索API
- `metasota_search` - MetaSota搜索API

## 📝 注意事项

1. **API密钥**：付费搜索引擎需要相应的API密钥，可以通过环境变量或直接传入
2. **时间范围**：不同搜索引擎对时间过滤的支持程度不同，建议结合客户端过滤
3. **并发限制**：某些API可能有并发请求限制，建议合理设置并发数量
4. **错误处理**：建议添加适当的错误处理，特别是网络请求失败的情况

## 🚀 性能优化建议

1. **合理设置文章数量**：根据需求设置合适的`max_articles`值
2. **选择合适的时间范围**：较短的时间范围通常返回更相关的结果
3. **使用缓存**：对于重复查询，建议启用缓存功能
4. **并发控制**：避免同时启动过多搜索引擎，以免触发API限制
