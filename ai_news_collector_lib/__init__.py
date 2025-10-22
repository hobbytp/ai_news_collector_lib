"""
AI News Collector Library
一个用于收集AI相关新闻的Python库

主要功能：
- 多源新闻搜索（HackerNews、ArXiv、DuckDuckGo等）
- 内容提取和关键词分析
- 结果去重和缓存
- 定时任务支持
- 灵活的配置系统

使用示例：
    from ai_news_collector_lib import AINewsCollector, SearchConfig

    config = SearchConfig(enable_hackernews=True, enable_arxiv=True)
    collector = AINewsCollector(config)
    result = await collector.collect_news("artificial intelligence")
"""

__version__ = "0.1.2"
__author__ = "AI News Collector Team"
__email__ = "support@ai-news-collector.com"

# 导入主要类和函数
from .core.collector import AINewsCollector
from .core.advanced_collector import AdvancedAINewsCollector
from .config.settings import SearchConfig, AdvancedSearchConfig
from .models.article import Article, AdvancedArticle
from .models.result import SearchResult
from .models.enhanced_query import EnhancedQuery
from .utils.cache import CacheManager
from .utils.reporter import ReportGenerator
from .utils.query_enhancer import QueryEnhancer, QueryEnhancerError, enhance_query_async

# 尝试导入可选的调度器（需要 schedule 包）
try:
    from .utils.scheduler import DailyScheduler
except ImportError:
    DailyScheduler = None

# 导出主要接口
__all__ = [
    # 核心类
    "AINewsCollector",
    "AdvancedAINewsCollector",
    # 配置类
    "SearchConfig",
    "AdvancedSearchConfig",
    # 数据模型
    "Article",
    "AdvancedArticle",
    "SearchResult",
    "EnhancedQuery",
    # 工具类
    "CacheManager",
    "ReportGenerator",
    "QueryEnhancer",
    "QueryEnhancerError",
    "enhance_query_async",
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
]

# 仅当 schedule 模块可用时导出 DailyScheduler
if DailyScheduler is not None:
    __all__.insert(-3, "DailyScheduler")

# 库信息
LIBRARY_INFO = {
    "name": "ai-news-collector-lib",
    "version": __version__,
    "description": "A Python library for collecting AI-related news from multiple sources",
    "author": __author__,
    "email": __email__,
    "license": "MIT",
    "homepage": "https://github.com/ai-news-collector/ai-news-collector-lib",
    "documentation": "https://ai-news-collector-lib.readthedocs.io/",
    "repository": "https://github.com/ai-news-collector/ai-news-collector-lib.git",
}


def get_library_info():
    """获取库信息"""
    return LIBRARY_INFO.copy()


def get_version():
    """获取版本信息"""
    return __version__
