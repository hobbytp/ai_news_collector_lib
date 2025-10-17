import os
import pytest
from dotenv import load_dotenv

# 加载本地 .env，以便测试根据环境开关网络等行为
load_dotenv()


@pytest.fixture(scope="session")
def allow_network() -> bool:
    """是否允许网络测试，由 .env 的 ALLOW_NETWORK 控制。"""
    return os.getenv("ALLOW_NETWORK", "0") == "1"


@pytest.fixture(scope="session")
def max_articles() -> int:
    return int(os.getenv("MAX_ARTICLES_PER_SOURCE", "3"))


@pytest.fixture(scope="session")
def days_back() -> int:
    return int(os.getenv("DAYS_BACK", "7"))


@pytest.fixture(scope="session")
def search_config(max_articles, days_back):
    from ai_news_collector_lib import SearchConfig
    cfg = SearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        enable_duckduckgo=True,
        enable_newsapi=False,
        max_articles_per_source=max_articles,
        days_back=days_back,
    )
    return cfg


@pytest.fixture(scope="session")
def collector(search_config):
    from ai_news_collector_lib import AINewsCollector
    return AINewsCollector(search_config)


@pytest.fixture(scope="session")
def advanced_config(max_articles, days_back):
    from ai_news_collector_lib import AdvancedSearchConfig
    cfg = AdvancedSearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        enable_duckduckgo=True,
        enable_newsapi=False,
        max_articles_per_source=max_articles,
        days_back=days_back,
        enable_content_extraction=False,  # 避免额外网络请求到内容页
        enable_keyword_extraction=True,
        cache_results=False,
    )
    return cfg


@pytest.fixture(scope="session")
def advanced_collector(advanced_config):
    from ai_news_collector_lib import AdvancedAINewsCollector
    return AdvancedAINewsCollector(advanced_config)