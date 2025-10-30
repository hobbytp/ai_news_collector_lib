"""
时间过滤功能测试

测试各个搜索引擎的时间过滤功能是否正常工作。
这个测试验证修复后的时间过滤功能能够正确过滤出指定时间范围内的文章。

使用方法：
1. 运行所有时间过滤测试：
   python -m pytest tests/test_date_filtering.py -v

2. 运行特定搜索引擎的时间过滤测试：
   python -m pytest tests/test_date_filtering.py::test_brave_search_date_filtering -v

3. 运行集成测试：
   python -m pytest tests/test_date_filtering.py::test_date_filtering_integration -v
"""

import os
import pytest
from datetime import datetime, timedelta, timezone
from typing import List

from ai_news_collector_lib.models.article import Article


def should_test_paid_apis() -> bool:
    """检查是否应该测试付费API"""
    test_paid = os.getenv("TEST_PAID_APIS", "0") == "1"
    cassette_dir = os.path.join(os.path.dirname(__file__), "cassettes")
    
    # 检查是否存在任何付费API的cassette
    paid_cassettes = [
        "tavily_search.yaml",
        "google_search.yaml", 
        "serper_search.yaml",
        "brave_search.yaml",
        "metasota_search.yaml",
        "newsapi_search.yaml",
    ]
    
    has_cassettes = any(
        os.path.exists(os.path.join(cassette_dir, c)) for c in paid_cassettes
    )
    
    return test_paid or has_cassettes


def check_articles_within_date_range(articles: List[Article], days_back: int) -> dict:
    """检查文章是否在指定时间范围内"""
    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=days_back)
    
    within_range = 0
    outside_range = 0
    invalid_dates = 0
    date_issues = []
    
    for article in articles:
        try:
            if not article.published:
                invalid_dates += 1
                continue
            
            # 处理不同的时间格式
            published_str = article.published
            if published_str.endswith("Z"):
                published_str = published_str[:-1] + "+00:00"
            
            published_time = datetime.fromisoformat(published_str)
            
            if published_time >= cutoff_date:
                within_range += 1
            else:
                outside_range += 1
                days_old = (now - published_time).days
                date_issues.append({
                    "title": article.title[:50] + "..." if len(article.title) > 50 else article.title,
                    "source": article.source,
                    "published": article.published,
                    "days_old": days_old
                })
                
        except (ValueError, TypeError) as e:
            invalid_dates += 1
            date_issues.append({
                "title": article.title[:50] + "..." if len(article.title) > 50 else article.title,
                "source": article.source,
                "error": f"日期解析失败: {e}",
                "published": article.published
            })
    
    return {
        "total": len(articles),
        "within_range": within_range,
        "outside_range": outside_range,
        "invalid_dates": invalid_dates,
        "date_issues": date_issues,
        "accuracy": (within_range / len(articles) * 100) if articles else 100
    }


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_brave_search_date_filtering(vcr_vcr):
    """测试 Brave Search API 的时间过滤功能"""
    from ai_news_collector_lib.tools.search_tools import BraveSearchTool
    
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "brave_search_date_filtering.yaml")
    ):
        pytest.skip("BRAVE_SEARCH_API_KEY 未配置且无cassette")
    
    tool = BraveSearchTool(api_key=api_key or "test-api-key", max_articles=5)
    
    with vcr_vcr.use_cassette("brave_search_date_filtering.yaml"):
        articles = tool.search("artificial intelligence", days_back=1)
    
    assert isinstance(articles, list)
    
    # 检查时间过滤效果
    date_check = check_articles_within_date_range(articles, 1)
    
    # 验证时间过滤效果 - 允许一定的容错率
    assert date_check["accuracy"] >= 80.0, f"时间过滤准确率只有 {date_check['accuracy']:.1f}%，低于80%阈值"
    
    # 如果准确率不是100%，记录详细信息
    if date_check["accuracy"] < 100.0:
        print(f"⚠️  {source} 时间过滤准确率: {date_check['accuracy']:.1f}%")
        if date_check['date_issues']:
            print(f"   超出范围的文章: {len(date_check['date_issues'])} 篇")


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_tavily_date_filtering(vcr_vcr):
    """测试 Tavily API 的时间过滤功能"""
    from ai_news_collector_lib.tools.search_tools import TavilyTool
    
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "tavily_date_filtering.yaml")
    ):
        pytest.skip("TAVILY_API_KEY 未配置且无cassette")
    
    tool = TavilyTool(api_key=api_key or "test-api-key", max_articles=5)
    
    with vcr_vcr.use_cassette("tavily_date_filtering.yaml"):
        articles = tool.search("machine learning", days_back=1)
    
    assert isinstance(articles, list)
    
    # 检查时间过滤效果
    date_check = check_articles_within_date_range(articles, 1)
    
    # 验证时间过滤效果 - 允许一定的容错率
    assert date_check["accuracy"] >= 80.0, f"时间过滤准确率只有 {date_check['accuracy']:.1f}%，低于80%阈值"
    
    # 如果准确率不是100%，记录详细信息
    if date_check["accuracy"] < 100.0:
        print(f"⚠️  {source} 时间过滤准确率: {date_check['accuracy']:.1f}%")
        if date_check['date_issues']:
            print(f"   超出范围的文章: {len(date_check['date_issues'])} 篇")


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_serper_date_filtering(vcr_vcr):
    """测试 Serper API 的时间过滤功能"""
    from ai_news_collector_lib.tools.search_tools import SerperTool
    
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "serper_date_filtering.yaml")
    ):
        pytest.skip("SERPER_API_KEY 未配置且无cassette")
    
    tool = SerperTool(api_key=api_key or "test-api-key", max_articles=5)
    
    with vcr_vcr.use_cassette("serper_date_filtering.yaml"):
        articles = tool.search("deep learning", days_back=1)
    
    assert isinstance(articles, list)
    
    # 检查时间过滤效果
    date_check = check_articles_within_date_range(articles, 1)
    
    # 验证时间过滤效果 - 允许一定的容错率
    assert date_check["accuracy"] >= 80.0, f"时间过滤准确率只有 {date_check['accuracy']:.1f}%，低于80%阈值"
    
    # 如果准确率不是100%，记录详细信息
    if date_check["accuracy"] < 100.0:
        print(f"⚠️  {source} 时间过滤准确率: {date_check['accuracy']:.1f}%")
        if date_check['date_issues']:
            print(f"   超出范围的文章: {len(date_check['date_issues'])} 篇")


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_newsapi_date_filtering(vcr_vcr):
    """测试 NewsAPI 的时间过滤功能"""
    from ai_news_collector_lib.tools.search_tools import NewsAPITool
    
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "newsapi_date_filtering.yaml")
    ):
        pytest.skip("NEWS_API_KEY 未配置且无cassette")
    
    tool = NewsAPITool(api_key=api_key or "test-api-key", max_articles=5)
    
    with vcr_vcr.use_cassette("newsapi_date_filtering.yaml"):
        articles = tool.search("AI technology", days_back=1)
    
    assert isinstance(articles, list)
    
    # 检查时间过滤效果
    date_check = check_articles_within_date_range(articles, 1)
    
    # 验证时间过滤效果 - 允许一定的容错率
    assert date_check["accuracy"] >= 80.0, f"时间过滤准确率只有 {date_check['accuracy']:.1f}%，低于80%阈值"
    
    # 如果准确率不是100%，记录详细信息
    if date_check["accuracy"] < 100.0:
        print(f"⚠️  {source} 时间过滤准确率: {date_check['accuracy']:.1f}%")
        if date_check['date_issues']:
            print(f"   超出范围的文章: {len(date_check['date_issues'])} 篇")


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_metasota_date_filtering(vcr_vcr):
    """测试 MetaSota API 的时间过滤功能"""
    from ai_news_collector_lib.tools.search_tools import MetaSotaSearchTool
    
    api_key = os.getenv("METASOSEARCH_API_KEY")
    if not api_key and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "metasota_date_filtering.yaml")
    ):
        pytest.skip("METASOSEARCH_API_KEY 未配置且无cassette")
    
    tool = MetaSotaSearchTool(api_key=api_key or "test-api-key", max_articles=5)
    
    with vcr_vcr.use_cassette("metasota_date_filtering.yaml"):
        articles = tool.search("neural networks", days_back=1)
    
    assert isinstance(articles, list)
    
    # 检查时间过滤效果
    date_check = check_articles_within_date_range(articles, 1)
    
    # 验证时间过滤效果 - 允许一定的容错率
    assert date_check["accuracy"] >= 80.0, f"时间过滤准确率只有 {date_check['accuracy']:.1f}%，低于80%阈值"
    
    # 如果准确率不是100%，记录详细信息
    if date_check["accuracy"] < 100.0:
        print(f"⚠️  {source} 时间过滤准确率: {date_check['accuracy']:.1f}%")
        if date_check['date_issues']:
            print(f"   超出范围的文章: {len(date_check['date_issues'])} 篇")


@pytest.mark.asyncio
async def test_hackernews_date_filtering(vcr_vcr):
    """测试 HackerNews 的时间过滤功能"""
    from ai_news_collector_lib.tools.search_tools import HackerNewsTool
    
    tool = HackerNewsTool(max_articles=5)
    
    with vcr_vcr.use_cassette("hackernews_date_filtering.yaml"):
        articles = tool.search("python", days_back=1)
    
    assert isinstance(articles, list)
    
    # 检查时间过滤效果
    date_check = check_articles_within_date_range(articles, 1)
    
    # 验证时间过滤效果 - 允许一定的容错率
    assert date_check["accuracy"] >= 80.0, f"时间过滤准确率只有 {date_check['accuracy']:.1f}%，低于80%阈值"
    
    # 如果准确率不是100%，记录详细信息
    if date_check["accuracy"] < 100.0:
        print(f"⚠️  {source} 时间过滤准确率: {date_check['accuracy']:.1f}%")
        if date_check['date_issues']:
            print(f"   超出范围的文章: {len(date_check['date_issues'])} 篇")


@pytest.mark.asyncio
async def test_arxiv_date_filtering(vcr_vcr):
    """测试 Arxiv 的时间过滤功能"""
    from ai_news_collector_lib.tools.search_tools import ArxivTool
    
    tool = ArxivTool(max_articles=5)
    
    with vcr_vcr.use_cassette("arxiv_date_filtering.yaml"):
        articles = tool.search("machine learning", days_back=1)
    
    assert isinstance(articles, list)
    
    # 检查时间过滤效果
    date_check = check_articles_within_date_range(articles, 1)
    
    # 验证时间过滤效果 - 允许一定的容错率
    assert date_check["accuracy"] >= 80.0, f"时间过滤准确率只有 {date_check['accuracy']:.1f}%，低于80%阈值"
    
    # 如果准确率不是100%，记录详细信息
    if date_check["accuracy"] < 100.0:
        print(f"⚠️  {source} 时间过滤准确率: {date_check['accuracy']:.1f}%")
        if date_check['date_issues']:
            print(f"   超出范围的文章: {len(date_check['date_issues'])} 篇")


@pytest.mark.asyncio
async def test_duckduckgo_date_filtering(vcr_vcr):
    """测试 DuckDuckGo 的时间过滤功能"""
    from ai_news_collector_lib.tools.search_tools import DuckDuckGoTool
    
    tool = DuckDuckGoTool(max_articles=5)
    
    with vcr_vcr.use_cassette("duckduckgo_date_filtering.yaml"):
        articles = tool.search("artificial intelligence", days_back=1)
    
    assert isinstance(articles, list)
    
    # 检查时间过滤效果
    date_check = check_articles_within_date_range(articles, 1)
    
    # 验证时间过滤效果 - 允许一定的容错率
    assert date_check["accuracy"] >= 80.0, f"时间过滤准确率只有 {date_check['accuracy']:.1f}%，低于80%阈值"
    
    # 如果准确率不是100%，记录详细信息
    if date_check["accuracy"] < 100.0:
        print(f"⚠️  {source} 时间过滤准确率: {date_check['accuracy']:.1f}%")
        if date_check['date_issues']:
            print(f"   超出范围的文章: {len(date_check['date_issues'])} 篇")


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_google_search_date_filtering(vcr_vcr):
    """测试 Google Search API 的时间过滤功能"""
    from ai_news_collector_lib.tools.search_tools import GoogleSearchTool
    
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    if not (api_key and engine_id) and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "google_search_date_filtering.yaml")
    ):
        pytest.skip("Google Search API 未配置且无cassette")
    
    tool = GoogleSearchTool(
        api_key=api_key or "test-api-key",
        search_engine_id=engine_id or "test-engine-id",
        max_articles=5
    )
    
    with vcr_vcr.use_cassette("google_search_date_filtering.yaml"):
        articles = tool.search("AI research", days_back=1)
    
    assert isinstance(articles, list)
    
    # 检查时间过滤效果
    date_check = check_articles_within_date_range(articles, 1)
    
    # 验证时间过滤效果 - 允许一定的容错率
    assert date_check["accuracy"] >= 80.0, f"时间过滤准确率只有 {date_check['accuracy']:.1f}%，低于80%阈值"
    
    # 如果准确率不是100%，记录详细信息
    if date_check["accuracy"] < 100.0:
        print(f"⚠️  {source} 时间过滤准确率: {date_check['accuracy']:.1f}%")
        if date_check['date_issues']:
            print(f"   超出范围的文章: {len(date_check['date_issues'])} 篇")


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_date_filtering_integration(vcr_vcr, allow_network):
    """集成测试：验证所有搜索引擎的时间过滤功能"""
    from ai_news_collector_lib import AINewsCollector, SearchConfig
    
    # 检查哪些API已配置
    has_tavily = bool(os.getenv("TAVILY_API_KEY"))
    has_google = bool(os.getenv("GOOGLE_SEARCH_API_KEY")) and bool(os.getenv("GOOGLE_SEARCH_ENGINE_ID"))
    has_serper = bool(os.getenv("SERPER_API_KEY"))
    has_brave = bool(os.getenv("BRAVE_SEARCH_API_KEY"))
    has_metasota = bool(os.getenv("METASOSEARCH_API_KEY"))
    has_newsapi = bool(os.getenv("NEWS_API_KEY"))
    
    # 如果没有配置任何付费API，检查是否有cassette
    cassette_exists = os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "date_filtering_integration.yaml")
    )
    
    if not any([has_tavily, has_google, has_serper, has_brave, has_metasota, has_newsapi]) and not cassette_exists:
        pytest.skip("无付费API配置且无cassette")
    
    # 创建配置，启用所有工具
    config = SearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        enable_duckduckgo=True,
        enable_tavily=has_tavily or cassette_exists,
        enable_google_search=has_google or cassette_exists,
        enable_serper=has_serper or cassette_exists,
        enable_brave_search=has_brave or cassette_exists,
        enable_metasota_search=has_metasota or cassette_exists,
        enable_newsapi=has_newsapi or cassette_exists,
        max_articles_per_source=2,
        days_back=1,  # 测试1天的时间过滤
    )
    
    collector = AINewsCollector(config)
    available_sources = collector.get_available_sources()
    
    if not available_sources:
        pytest.skip("没有可用的搜索源")
    
    with vcr_vcr.use_cassette("date_filtering_integration.yaml"):
        result = await collector.collect_news(query="AI technology")
    
    assert result is not None
    assert result.total_articles > 0
    
    # 检查所有文章的时间过滤效果
    date_check = check_articles_within_date_range(result.articles, 1)
    
    # 验证时间过滤效果 - 允许一定的容错率，因为某些API可能返回稍微超出范围的文章
    assert date_check["accuracy"] >= 80.0, f"时间过滤准确率只有 {date_check['accuracy']:.1f}%，低于80%阈值"
    
    # 如果准确率不是100%，记录详细信息用于调试
    if date_check["accuracy"] < 100.0:
        print(f"⚠️  时间过滤准确率: {date_check['accuracy']:.1f}%")
        print(f"   总文章数: {date_check['total']}")
        print(f"   时间范围内: {date_check['within_range']}")
        print(f"   超出范围: {date_check['outside_range']}")
        if date_check['date_issues']:
            print("   超出范围的文章:")
            for issue in date_check['date_issues'][:3]:  # 只显示前3个
                print(f"     - {issue.get('title', 'Unknown')} ({issue.get('days_old', 'Unknown')}天前)")
    
    # 验证每个返回了文章的源，其文章都在时间范围内
    sources_with_articles = {a.source for a in result.articles}
    for source in sources_with_articles:
        source_articles = [a for a in result.articles if a.source == source]
        assert len(source_articles) > 0, f"源 {source} 没有返回文章"
        
        # 验证该源的文章都在时间范围内
        source_date_check = check_articles_within_date_range(source_articles, 1)
        assert source_date_check["outside_range"] == 0, f"源 {source} 有 {source_date_check['outside_range']} 篇超出时间范围的文章"

    # 警告那些在可用源中但没有返回文章的源
    sources_without_articles = set(available_sources) - sources_with_articles
    if sources_without_articles:
        print(f"\n⚠️ 警告: 以下源被启用但没有返回任何文章: {', '.join(sources_without_articles)}")
        print("   这在离线 VCR 测试中可能是正常的，因为请求匹配策略忽略了查询参数。")


@pytest.mark.asyncio
async def test_different_time_ranges(vcr_vcr):
    """测试不同时间范围的时间过滤功能"""
    from ai_news_collector_lib import AINewsCollector, SearchConfig
    
    # 测试不同的时间范围
    time_ranges = [1, 7, 30]
    
    for days_back in time_ranges:
        config = SearchConfig(
            enable_hackernews=True,
            enable_arxiv=True,
            enable_duckduckgo=True,
            max_articles_per_source=3,
            days_back=days_back,
        )
        
        collector = AINewsCollector(config)
        
        with vcr_vcr.use_cassette(f"time_range_{days_back}_days.yaml"):
            result = await collector.collect_news(query="technology")
        
        assert result is not None
        assert result.total_articles > 0
        
        # 检查时间过滤效果
        date_check = check_articles_within_date_range(result.articles, days_back)
        
        # 验证所有文章都在指定时间范围内
        assert date_check["outside_range"] == 0, f"在 {days_back} 天范围内发现 {date_check['outside_range']} 篇超出时间范围的文章"
        assert date_check["accuracy"] == 100.0, f"在 {days_back} 天范围内时间过滤准确率只有 {date_check['accuracy']:.1f}%"
