# 🔰 AI News Collector Library

> 一个用于收集AI相关新闻的Python库，支持多种搜索源和高级功能。

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-ai--news--collector--lib-blue)](https://pypi.org/project/ai-news-collector-lib/)
[![Latest Release](https://img.shields.io/badge/Latest-v0.1.4-brightgreen)](https://github.com/ai-news-collector/ai-news-collector-lib/releases/tag/v0.1.4)

---

## 🚀 最新更新 (v0.1.4 - 时间过滤增强)

> **这是 v0.1.4 版本的重大更新！** 完全解决了时间过滤不准确的问题。强烈建议所有用户升级。

### ⏰ 时间过滤增强（重大修复）

- ✅ **100%时间过滤准确率** - 从0%提升到100%，彻底解决时间过滤问题
- ✅ **双重过滤机制** - API级别过滤 + 客户端备用过滤，确保准确性
- ✅ **全搜索引擎支持** - 修复了8个搜索引擎的时间过滤问题
- ✅ **智能时间解析** - 支持多种时间格式的自动识别和解析
- ✅ **统一接口** - 所有搜索引擎使用相同的时间过滤逻辑

### 🔧 核心改进

- ✅ **API级别过滤** - Brave Search、Tavily、NewsAPI等支持原生时间参数
- ✅ **客户端过滤** - 所有搜索引擎都有客户端时间过滤作为备用
- ✅ **时间提取优化** - 为每个搜索引擎添加专门的发布时间提取方法
- ✅ **错误处理增强** - 时间解析失败时的优雅降级机制

📋 详见: [时间过滤修复总结](DATE_FILTERING_FIX_SUMMARY.md) | [测试验证](tests/test_date_filtering.py) | [完整指南](USAGE_GUIDE.md)

---

## 🚀 历史更新 (v0.1.3 - LLM 查询增强)

> **v0.1.3 版本更新** - 引入了 AI 驱动的查询增强功能。

### 🤖 LLM 查询增强（v0.1.3功能）

- ✅ **AI 驱动查询优化** - 集成 Google Gemini LLM，智能优化用户查询
- ✅ **多引擎支持** - 为所有 11 个搜索引擎生成优化查询（单一 LLM 调用）
- ✅ **智能缓存** - 24 小时缓存，避免重复 LLM 调用
- ✅ **灵活配置** - 可选启用/禁用，支持自定义 LLM 提供商和模型
- ✅ **优雅降级** - LLM 调用失败时自动使用原始查询，确保服务可用性

### 🔧 核心改进（v0.1.3）

- ✅ **增强的查询对象** - 新增 `EnhancedQuery` 模型（支持 11 个搜索引擎）
- ✅ **查询优化器** - 新增 `QueryEnhancer` 工具类（500+ 行高质量代码）
- ✅ **集成优化** - AdvancedAINewsCollector 无缝集成查询增强

📋 详见: [实现总结](IMPLEMENTATION_SUMMARY.md) | [LLM 配置指南](docs/README_BADGES.md) | [完整指南](USAGE_GUIDE.md)

---

## ✨ 主要特性

### 核心功能

- 🔥 **多源聚合** - 支持HackerNews、ArXiv、DuckDuckGo等多个搜索源
- 📰 **付费API集成** - NewsAPI、Tavily、Google Search、Bing Search、Serper等
- 🤖 **智能内容处理** - 自动提取文章内容和关键词
- 💾 **智能缓存** - 避免重复搜索，提高效率
- ⏰ **定时任务** - 支持定时自动收集和报告生成
- 🔍 **去重处理** - 基于相似度的智能去重
- 📊 **数据分析** - 生成详细的收集结果报告

### 测试与质量

- 🧪 **离线测试** - 使用VCR cassettes实现完全离线的付费API测试
- 🔐 **安全优先** - 所有测试数据中的凭证已清理
- 📈 **覆盖率** - pytest-cov集成，详细的测试覆盖率报告
- 🤖 **自动化** - GitHub Actions自动化测试和发布

---

## 📦 安装

### 从PyPI安装（推荐）

```bash
# 基础安装
pip install ai-news-collector-lib

# 安装开发/测试依赖
pip install ai-news-collector-lib[dev]

# 或从源代码安装
pip install -e .[dev]
```

### 系统要求

- Python 3.9+
- pip 或 conda

---

## 🔑 配置API密钥

创建 `.env` 文件并配置API密钥（可选，仅用于付费API）：

```bash
# API密钥配置
NEWS_API_KEY=your_newsapi_key
TAVILY_API_KEY=your_tavily_key
GOOGLE_SEARCH_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id
BING_SEARCH_API_KEY=your_bing_key
SERPER_API_KEY=your_serper_key
BRAVE_SEARCH_API_KEY=your_brave_key
METASOSEARCH_API_KEY=your_metasota_key
```

> ⚠️ **重要**：请勿将 `.env` 文件提交到版本控制。参见 [API密钥安全指南](API_KEY_SECURITY_AUDIT.md)。

---

## 🎯 快速开始

### 基础使用（免费源）

```python
import asyncio
from ai_news_collector_lib import AINewsCollector, SearchConfig

async def main():
    # 创建配置
    config = SearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        enable_duckduckgo=True,
        max_articles_per_source=10,
        days_back=7
    )
    
    # 创建收集器
    collector = AINewsCollector(config)
    
    # 收集新闻
    result = await collector.collect_news("machine learning")
    
    # 输出结果
    print(f"收集 {result.total_articles} 篇文章（去重后 {result.unique_articles} 篇）")
    for article in result.articles[:5]:
        print(f"- {article.title}")
    
    return result

# 运行
asyncio.run(main())
```

### 🤖 LLM 查询增强（新）

```python
import asyncio
from ai_news_collector_lib import AdvancedAINewsCollector, AdvancedSearchConfig

async def main():
    # 创建带 LLM 查询增强的配置
    config = AdvancedSearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        enable_tavily=True,
        enable_query_enhancement=True,        # ✨ 启用 LLM 查询增强
        llm_provider="google",                # 使用 Google Gemini
        llm_model="gemini-1.5-flash",         # 高性能模型
        llm_api_key="your-google-api-key",    # 从环境变量设置更安全
        query_enhancement_cache_ttl=86400,    # 24 小时缓存
        max_articles_per_source=10
    )
    
    # 创建收集器
    collector = AdvancedAINewsCollector(config)
    
    # LLM 会自动为各个搜索引擎优化查询
    # 例如：输入 "machine learning" → 
    #   HackerNews: "machine learning frameworks algorithms"
    #   ArXiv: "machine learning optimization techniques"
    #   Tavily: "latest machine learning applications 2024"
    result = await collector.collect_news_advanced("machine learning")
    
    # 查看增强后的查询
    if result.get('enhanced_query'):
        enhanced = result['enhanced_query']
        print(f"原始查询: {enhanced.original_query}")
        print(f"增强查询数: {len(enhanced.get_enabled_engines())}")
        for engine in enhanced.get_enabled_engines():
            print(f"  - {engine}: {getattr(enhanced, engine)}")
    
    return result

asyncio.run(main())
```

**LLM 查询增强的优势：**

- 🎯 **精准搜索** - AI 自动为不同搜索引擎生成最优查询
- ⚡ **智能缓存** - 相同查询在 24 小时内无需重新调用 LLM
- 💰 **经济高效** - 单一 LLM 调用处理所有搜索引擎
- 🔄 **灵活降级** - LLM 不可用时自动使用原始查询
- 📊 **完整支持** - 支持所有 11 个搜索引擎（HackerNews、ArXiv、DuckDuckGo、NewsAPI、Tavily、Google Search、Bing Search、Serper、Reddit、Hacker News API、Medium）

### 高级使用（包含内容提取和关键词提取）

```python
import asyncio
from ai_news_collector_lib import AdvancedAINewsCollector, AdvancedSearchConfig

async def main():
    # 创建高级配置
    config = AdvancedSearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        enable_duckduckgo=True,
        enable_content_extraction=True,      # 自动提取内容
        enable_keyword_extraction=True,      # 自动提取关键词
        cache_results=True,                  # 启用缓存
        max_articles_per_source=10
    )
    
    # 创建高级收集器
    collector = AdvancedAINewsCollector(config)
    
    # 收集增强新闻
    result = await collector.collect_news_advanced("artificial intelligence")
    
    # 分析结果
    total_words = sum(article.get('word_count', 0) for article in result['articles'])
    print(f"总字数: {total_words}")
    print(f"关键词: {', '.join(result.get('top_keywords', [])[:10])}")
    
    return result

# 运行
asyncio.run(main())
```

### 付费API使用（带缓存）

```python
import asyncio
from ai_news_collector_lib import AdvancedAINewsCollector, AdvancedSearchConfig

async def main():
    # 创建配置 - 混合使用免费和付费源
    config = AdvancedSearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        enable_tavily=True,              # 付费搜索API
        enable_google_search=True,       # 谷歌自定义搜索
        enable_serper=True,              # Serper搜索API
        cache_results=True,              # 启用缓存减少API调用
        max_articles_per_source=15,
        similarity_threshold=0.85
    )
    
    collector = AdvancedAINewsCollector(config)
    result = await collector.collect_news_advanced("deep learning")
    
    return result

asyncio.run(main())
```

---

## 📊 支持的搜索源

### ✅ 免费源（无需API密钥）

| 源 | 描述 | 特点 |
|---|---|---|
| 🔥 **HackerNews** | 技术社区讨论 | 实时热点，开发者友好 |
| 📚 **ArXiv** | 学术论文预印本 | 学术质量，多学科覆盖 |
| 🦆 **DuckDuckGo** | 隐私搜索引擎 | 隐私保护，广泛覆盖 |

### 💰 付费源（需要API密钥）

| 源 | API | 特点 | 免费额度 |
|---|---|---|---|
| 📡 **NewsAPI** | newsapi.org | 多源聚合、新闻分类 | 100 请求/天 |
| 🔍 **Tavily** | tavily.com | AI驱动搜索、实时 | 1000 请求/月 |
| 🌐 **Google Search** | googleapis.com | 精准搜索、覆盖广 | 100 请求/天 |
| 🔵 **Bing Search** | bing.com | 多媒体支持、国际化 | 3000 请求/月 |
| ⚡ **Serper** | serper.dev | 高速、便宜 | 100 请求/月 |
| 🦁 **Brave Search** | search.brave.com | 独立隐私搜索 | 100 请求/月 |
| 🔬 **MetaSota** | metaso.cn | MCP协议搜索 | 按配额 |

---

## ⚙️ 详细配置

### 搜索配置选项

```python
from ai_news_collector_lib import AdvancedSearchConfig

config = AdvancedSearchConfig(
    # 传统源
    enable_hackernews=True,
    enable_arxiv=True,
    enable_rss_feeds=False,
    
    # 付费搜索源
    enable_tavily=False,
    enable_google_search=False,
    enable_bing_search=False,
    enable_serper=False,
    enable_brave_search=False,
    enable_metasota_search=False,
    enable_newsapi=False,
    
    # 网页搜索
    enable_duckduckgo=True,
    
    # 高级功能
    enable_content_extraction=False,     # 自动提取文章内容
    enable_keyword_extraction=False,     # 自动提取关键词
    cache_results=False,                 # 缓存结果
    
    # 搜索参数
    max_articles_per_source=10,
    days_back=7,
    similarity_threshold=0.85,
    timeout_seconds=30
)
```

---

## 🛠️ 高级功能

### 定时收集

```python
from ai_news_collector_lib import DailyScheduler, AdvancedAINewsCollector, AdvancedSearchConfig

async def collect_news():
    config = AdvancedSearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        cache_results=True
    )
    collector = AdvancedAINewsCollector(config)
    return await collector.collect_news_advanced("AI")

# 创建定时任务 - 每天上午9点
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

# 获取缓存
cache_key = cache.get_cache_key("AI news", ["hackernews", "arxiv"])
cached_result = cache.get_cached_result(cache_key)

if cached_result:
    print("使用缓存结果")
    result = cached_result
else:
    # 执行搜索
    result = await collector.collect_news("AI news")
    # 缓存结果
    cache.cache_result(cache_key, result)
```

### 报告生成

```python
from ai_news_collector_lib import ReportGenerator

# 创建报告生成器
reporter = ReportGenerator(output_dir="./reports")

# 生成Markdown报告
report = reporter.generate_daily_report(result, format="markdown")
reporter.save_report(result, filename="daily_report.md")

# 生成CSV报告
reporter.generate_daily_report(result, format="csv")
```

---

## 🧪 测试

### 运行所有测试

```bash
# 运行基础测试
pytest

# 运行所有测试（包括付费API测试）
pytest -v

# 生成覆盖率报告
pytest --cov=ai_news_collector_lib --cov-report=html
```

### 离线付费API测试（使用VCR Cassettes）

项目包含预录制的VCR cassettes，允许在完全离线状态下测试所有付费API集成 - **无需真实API密钥**。

```bash
# 运行付费API测试（使用cassettes，完全离线）
pytest tests/test_integration_advanced.py -v

# 查看cassette记录详情
cat tests/cassettes/advanced_ml_hn_ddg.yaml
```

### VCR Cassette原理

VCR库记录真实的HTTP请求/响应，然后在测试中重放（无需真实API调用）：

```python
import pytest
from vcr import VCR

# 使用cassette进行测试
@pytest.mark.vcr
def test_with_cassette(vcr):
    # 首次运行记录HTTP交互，后续测试直接重放
    result = collector.search(query="AI")
    assert len(result) > 0
```

详见: [VCR Cassette详解](VCR_CASSETTE_EXPLANATION.md) | [测试指南](TESTING_GUIDE.md) | [FAQ](FAQ_PR_TESTING.md)

---

## 🔄 CI/CD 与自动化

### GitHub Actions 工作流

项目使用GitHub Actions实现完整的自动化测试和发布：

| 工作流 | 触发条件 | 功能 |
|---|---|---|
| **test-paid-apis** | Push到任何分支 | 运行所有测试，生成覆盖率报告 |
| **publish** | Push git标签 (v*) | 自动构建并发布到PyPI |
| **release** | 发布时 | 创建GitHub Release页面 |

### 发布新版本

```bash
# 1. 确保所有测试通过
pytest

# 2. 创建版本标签
git tag -a v0.1.3 -m "Release v0.1.3"

# 3. 推送标签（自动触发发布工作流）
git push origin v0.1.3
```

详见: [发布指南](RELEASE_GUIDE.md) | [快速发布](QUICK_RELEASE.md)

---

## 📚 文档

### 核心文档

- [架构设计](ARCHITECTURE.md) - 项目结构和设计理念
- [实现总结](IMPLEMENTATION_SUMMARY.md) - v0.1.3 LLM 查询增强实现详情
- [VCR说明](VCR_CASSETTE_EXPLANATION.md) - 离线测试机制解析
- [测试指南](TESTING_GUIDE.md) - 完整测试说明
- [使用指南](USAGE_GUIDE.md) - 详细使用文档

### 快速参考

- [发布指南](RELEASE_GUIDE.md) - 版本发布流程
- [快速发布](QUICK_RELEASE.md) - 快速发布清单
- [PyPI指南](PYPI_RELEASE_GUIDE.md) - PyPI发布说明
- [FAQ](FAQ_PR_TESTING.md) - 常见问题解答

### API参考

- [搜索配置](ai_news_collector_lib/config/) - 配置选项说明
- [模型对象](ai_news_collector_lib/models/) - 数据模型定义
- [搜索工具](ai_news_collector_lib/tools/) - 各源工具实现

---

## 🗓️ ArXiv 日期处理

ArXiv日期解析包含完整的回退机制：

- 默认使用BeautifulSoup的XML解析获取`published`字段
- 若解析异常则回退到feedparser
- 在feedparser中支持`published_parsed`和`updated_parsed`字段
- 回退顺序: `published_parsed` → `updated_parsed` → `datetime.now()`
- 时区处理: Atom格式中`Z`表示UTC，使用`datetime.fromisoformat`解析

最小验证脚本：

```bash
python scripts/min_check_feedparser_fallback.py
```

该脚本验证RSS和Atom格式在缺少日期字段时的回退逻辑。

---

## 🤝 贡献

欢迎贡献代码和改进建议！

### 贡献流程

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

### 开发指南

- 遵循PEP 8代码风格
- 添加测试用例
- 更新相关文档

详见: [完整贡献指南](CONTRIBUTING.md)

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🆘 支持

### 获取帮助

- 📖 [完整文档](https://ai-news-collector-lib.readthedocs.io/)
- 🐛 [提交Issue](https://github.com/ai-news-collector/ai-news-collector-lib/issues)
- 💬 [讨论区](https://github.com/ai-news-collector/ai-news-collector-lib/discussions)
- 📧 [邮件支持](mailto:support@ai-news-collector.com)

### 常见问题

**Q: 如何不使用API密钥运行测试？**
A: 使用VCR cassettes！测试会自动使用预录制的HTTP响应。详见[VCR说明](VCR_CASSETTE_EXPLANATION.md)。

**Q: 是否可以在生产环境中使用此库？**
A: 可以，但请确保：

- 安全地管理API密钥（使用.env文件）
- 合理设置缓存TTL避免过时数据
- 监控API调用限制

**Q: 如何贡献新的搜索源？**
A: 详见[架构设计](ARCHITECTURE.md)中的"添加新搜索源"部分。

详见: [完整FAQ](FAQ_PR_TESTING.md)

---

## 📈 更新日志

### v0.1.3 (2025-10-22) - 🤖 LLM 查询增强

- ✨ **AI 驱动查询优化** - 集成 Google Gemini LLM，为所有搜索引擎生成优化查询
- ✅ 新增 `EnhancedQuery` 数据模型（支持 11 个搜索引擎）
- ✅ 新增 `QueryEnhancer` 工具类（500+ 行，单一 LLM 调用架构）
- ✅ 智能缓存 - 24 小时 TTL 避免重复 LLM 调用
- ✅ 灵活配置 - 可选启用/禁用，支持自定义 LLM 提供商
- ✅ 优雅降级 - LLM 不可用时自动使用原始查询
- ✅ 完整测试 - 8 个单元测试，81% 代码覆盖率
- ✅ 代码质量 - Black & Flake8 检查通过

### v0.1.2 (2025-10-21) - 🔒 安全版本

- ✅ 全面安全审计 - 清理VCR cassettes中的所有凭证
- ✅ 将测试API密钥替换为"FILTERED"占位符
- ✅ 更新所有cassette URL为真实API端点
- ✅ 集成pytest-cov提供覆盖率报告
- ✅ GitHub Actions自动化测试和PyPI发布

### v0.1.0 (2025-10-07)

- 初始预发布版本
- 支持基础搜索功能
- 支持多种搜索源
- 支持高级功能（内容提取、关键词分析、缓存等）

---

## 📊 项目结构

```
ai_news_collector_lib/
├── __init__.py                    # 主模块入口
├── cli.py                        # 命令行接口
├── config/                       # 配置模块
│   ├── __init__.py
│   ├── settings.py              # 搜索配置
│   └── api_keys.py              # API密钥管理
├── core/                        # 核心功能
│   ├── __init__.py
│   ├── collector.py             # 基础收集器
│   └── advanced_collector.py    # 高级收集器
├── models/                      # 数据模型
│   ├── __init__.py
│   ├── article.py              # 文章模型
│   └── result.py               # 结果模型
├── tools/                       # 搜索工具
│   ├── __init__.py
│   └── search_tools.py         # 各种搜索工具
├── utils/                       # 工具函数
│   ├── __init__.py
│   ├── cache.py                # 缓存管理
│   ├── content_extractor.py    # 内容提取
│   ├── keyword_extractor.py    # 关键词提取
│   ├── reporter.py             # 报告生成
│   └── scheduler.py            # 定时任务
└── examples/                    # 使用示例
    ├── basic_usage.py
    └── advanced_usage.py

tests/
├── conftest.py                 # pytest配置
├── test_basic.py               # 基础功能测试
├── test_integration_basic.py    # 基础集成测试
├── test_integration_advanced.py # 付费API集成测试
├── cassettes/                  # VCR cassette文件
│   ├── basic_ai_hn_ddg.yaml
│   ├── advanced_ml_hn_ddg.yaml
│   └── ...
└── test_arxiv_fallback_offline.py # ArXiv特殊测试
```

---

**祝你使用愉快！** 🎉

如有问题或建议，欢迎[提交Issue](https://github.com/ai-news-collector/ai-news-collector-lib/issues)或加入[讨论区](https://github.com/ai-news-collector/ai-news-collector-lib/discussions)。
