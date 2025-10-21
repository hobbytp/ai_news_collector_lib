"""
付费API工具测试

使用方法：
1. 首次运行（录制请求）：
   在 .env 中设置：
   ALLOW_NETWORK=1
   TEST_PAID_APIS=1
   UPDATE_CASSETTES=1  # 可选，强制重新录制

   然后运行：
   python -m pytest tests/test_paid_apis.py -v

2. 后续运行（使用录制的cassette）：
   不需要设置 ALLOW_NETWORK 或 TEST_PAID_APIS
   直接运行即可：
   python -m pytest tests/test_paid_apis.py -v

注意：
- 首次运行会消耗少量API配额（每个工具~1个请求）
- 录制后的cassette可以无限次离线回放
- 所有API密钥从 .env 读取
"""

import os
import pytest
from datetime import datetime


def should_test_paid_apis() -> bool:
    """
    检查是否应该测试付费API。
    如果存在对应的cassette文件，即使没有设置环境变量也可以测试。
    """
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


# 如果没有配置付费API测试且没有cassettes，跳过所有测试
pytestmark = pytest.mark.skipif(
    not should_test_paid_apis(),
    reason="付费API测试未启用。设置 TEST_PAID_APIS=1 或确保cassettes存在"
)


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_tavily_search(vcr_vcr):
    """测试 Tavily API 搜索"""
    from ai_news_collector_lib.tools.search_tools import TavilyTool

    # 检查API密钥
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "tavily_search.yaml")
    ):
        pytest.skip("TAVILY_API_KEY 未配置且无cassette")

    # 使用实际密钥或占位符（cassette会自动过滤）
    tool = TavilyTool(api_key=api_key or "test-api-key", max_articles=3)

    with vcr_vcr.use_cassette("tavily_search.yaml"):
        articles = tool.search("artificial intelligence", days_back=7)

    # 基础验证
    assert isinstance(articles, list)
    if articles:  # 可能没有结果
        article = articles[0]
        assert article.title
        assert article.url
        assert article.source == "tavily"
        # Tavily API返回的source_name是实际的域名（从URL提取）
        assert article.source_name
        assert article.source_name in ["www.coursera.org", "en.wikipedia.org", "cloud.google.com"]
        # 验证日期格式
        datetime.fromisoformat(article.published.replace("Z", "+00:00"))


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_google_search(vcr_vcr):
    """测试 Google Custom Search API"""
    from ai_news_collector_lib.tools.search_tools import GoogleSearchTool

    # 检查API密钥
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    if (not api_key or not search_engine_id) and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "google_search.yaml")
    ):
        pytest.skip("Google API 凭证未配置且无cassette") 

    tool = GoogleSearchTool(
        api_key=api_key or "test-api-key",
        search_engine_id=search_engine_id or "test-engine-id",
        max_articles=3
    )

    with vcr_vcr.use_cassette("google_search.yaml"):
        articles = tool.search("machine learning", days_back=7)

    assert isinstance(articles, list)
    if articles:
        article = articles[0]
        assert article.title
        assert article.url
        assert article.source == "google_search"
        # Google API返回的source_name是displayLink（域名）
        assert article.source_name
        assert article.source_name in ["www.nature.com", "www.sciencedaily.com", "www.example.com"]
        datetime.fromisoformat(article.published.replace("Z", "+00:00"))


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_serper_search(vcr_vcr):
    """测试 Serper API 搜索"""
    from ai_news_collector_lib.tools.search_tools import SerperTool

    api_key = os.getenv("SERPER_API_KEY")
    if not api_key and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "serper_search.yaml")
    ):
        pytest.skip("SERPER_API_KEY 未配置且无cassette")

    tool = SerperTool(api_key=api_key or "test-api-key", max_articles=3)

    with vcr_vcr.use_cassette("serper_search.yaml"):
        articles = tool.search("deep learning", days_back=7)

    assert isinstance(articles, list)
    if articles:
        article = articles[0]
        assert article.title
        assert article.url
        assert article.source == "serper"
        # Serper API返回的source_name是从URL提取的域名
        assert article.source_name
        assert article.source_name in ["en.wikipedia.org", "www.deeplearning.ai", "www.ibm.com"]
        datetime.fromisoformat(article.published.replace("Z", "+00:00"))


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_brave_search(vcr_vcr):
    """测试 Brave Search API"""
    from ai_news_collector_lib.tools.search_tools import BraveSearchTool

    api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "brave_search.yaml")
    ):
        pytest.skip("BRAVE_SEARCH_API_KEY 未配置且无cassette")

    tool = BraveSearchTool(api_key=api_key or "test-api-key", max_articles=3)

    with vcr_vcr.use_cassette("brave_search.yaml"):
        articles = tool.search("neural networks", days_back=7)

        assert isinstance(articles, list)
        if articles:
            article = articles[0]
            assert article.title
            assert article.url
            assert article.source == "brave_search"
            # Brave API返回的source_name是从URL提取的域名
            assert article.source_name
            assert article.source_name in ["en.wikipedia.org", "www.example.com", "github.com"]
            datetime.fromisoformat(article.published.replace("Z", "+00:00"))
@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_metasota_search(vcr_vcr):
    """测试 MetaSota API 搜索"""
    from ai_news_collector_lib.tools.search_tools import MetaSotaSearchTool

    api_key = os.getenv("METASOSEARCH_API_KEY")
    if not api_key and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "metasota_search.yaml")
    ):
        pytest.skip("METASOSEARCH_API_KEY 未配置且无cassette")

    tool = MetaSotaSearchTool(api_key=api_key or "test-api-key", max_articles=3)

    with vcr_vcr.use_cassette("metasota_search.yaml"):
        articles = tool.search("computer vision", days_back=7)

    assert isinstance(articles, list)
    if articles:
        article = articles[0]
        assert article.title
        assert article.url
        assert article.source == "metasota_search"
        # MetaSota API返回的source_name就是source字段值（'MetaSota'）
        assert article.source_name == "MetaSota"
        datetime.fromisoformat(article.published.replace("Z", "+00:00"))


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_newsapi_search(vcr_vcr):
    """测试 NewsAPI 搜索"""
    from ai_news_collector_lib.tools.search_tools import NewsAPITool

    api_key = os.getenv("NEWS_API_KEY")
    if not api_key and not os.path.exists(
        os.path.join(os.path.dirname(__file__), "cassettes", "newsapi_search.yaml")
    ):
        pytest.skip("NEWS_API_KEY 未配置且无cassette")

    tool = NewsAPITool(api_key=api_key or "test-api-key", max_articles=3)

    with vcr_vcr.use_cassette("newsapi_search.yaml"):
        articles = tool.search("artificial intelligence", days_back=7)

    assert isinstance(articles, list)
    if articles:
        article = articles[0]
        assert article.title
        assert article.url
        assert article.source == "newsapi"
        # NewsAPI返回的source_name是实际的新闻源名称，如"TheStreet"、"CNN"等
        assert article.source_name
        assert len(article.source_name) > 0  # 任何非空字符串都可以
        datetime.fromisoformat(article.published.replace("Z", "+00:00"))


@pytest.mark.asyncio
@pytest.mark.paid_api
async def test_paid_apis_integration(vcr_vcr, allow_network):
    """
    集成测试：使用所有配置的付费API工具进行搜索
    这个测试会自动检测哪些API已配置，只测试已配置的
    """
    from ai_news_collector_lib import AINewsCollector, SearchConfig

    # 检查哪些API已配置
    has_tavily = bool(os.getenv("TAVILY_API_KEY"))
    has_google = bool(os.getenv("GOOGLE_SEARCH_API_KEY")) and bool(
        os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    )
    has_serper = bool(os.getenv("SERPER_API_KEY"))
    has_brave = bool(os.getenv("BRAVE_SEARCH_API_KEY"))
    has_metasota = bool(os.getenv("METASOSEARCH_API_KEY"))
    has_newsapi = bool(os.getenv("NEWS_API_KEY"))

    # 如果没有配置任何付费API，检查是否有cassette
    cassette_exists = os.path.exists(
        os.path.join(
            os.path.dirname(__file__), "cassettes", "paid_apis_integration.yaml"
        )
    )

    if not any([
        has_tavily, has_google, has_serper,
        has_brave, has_metasota, has_newsapi
    ]) and not cassette_exists:
        pytest.skip("无付费API配置且无cassette")

    # 创建配置，启用所有付费工具
    config = SearchConfig(
        enable_hackernews=False,  # 仅测试付费API
        enable_arxiv=False,
        enable_duckduckgo=False,
        enable_tavily=has_tavily or cassette_exists,
        enable_google_search=has_google or cassette_exists,
        enable_serper=has_serper or cassette_exists,
        enable_brave_search=has_brave or cassette_exists,
        enable_metasota_search=has_metasota or cassette_exists,
        enable_newsapi=has_newsapi or cassette_exists,
        max_articles_per_source=2,
        days_back=7,
    )

    collector = AINewsCollector(config)
    available_sources = collector.get_available_sources()

    # 只有在有可用源时才进行测试
    if not available_sources:
        pytest.skip("没有可用的付费API源")

    with vcr_vcr.use_cassette("paid_apis_integration.yaml"):
        result = await collector.collect_news(
            query="AI news",
            sources=available_sources
        )

    # 验证结果结构
    assert isinstance(result.total_articles, int)
    assert isinstance(result.unique_articles, int)
    assert isinstance(result.source_progress, dict)

    # 验证至少有一个源成功
    successful_sources = [
        s for s, p in result.source_progress.items()
        if p["status"] == "completed"
    ]
    assert len(successful_sources) > 0, (
        f"没有任何付费API源成功。"
        f"可用源: {available_sources}, "
        f"源状态: {result.source_progress}"
    )

    # 如果有文章，验证基本字段
    if result.articles:
        article = result.articles[0]
        assert article.title
        assert article.url
        assert article.source in available_sources
