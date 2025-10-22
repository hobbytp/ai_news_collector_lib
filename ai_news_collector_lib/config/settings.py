"""
配置设置
定义搜索配置和高级配置的数据结构
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class SearchConfig:
    """基础搜索配置"""

    # 传统源
    enable_hackernews: bool = True
    enable_arxiv: bool = True
    enable_newsapi: bool = False
    enable_rss_feeds: bool = True

    # 搜索引擎源
    enable_duckduckgo: bool = True
    enable_tavily: bool = False
    enable_google_search: bool = False
    enable_bing_search: bool = False
    enable_serper: bool = False
    enable_brave_search: bool = False
    enable_metasota_search: bool = False

    # API密钥
    newsapi_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    google_search_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None
    bing_search_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    brave_search_api_key: Optional[str] = None
    metasota_search_api_key: Optional[str] = None

    # 搜索参数
    max_articles_per_source: int = 10
    days_back: int = 7
    similarity_threshold: float = 0.85

    def __post_init__(self):
        """初始化后处理"""
        # 从环境变量加载API密钥
        self._load_from_env()

        # 自动启用有API密钥的源
        self._auto_enable_sources()

    def _load_from_env(self):
        """从环境变量加载配置"""
        if not self.newsapi_key:
            self.newsapi_key = os.getenv("NEWS_API_KEY")

        if not self.tavily_api_key:
            self.tavily_api_key = os.getenv("TAVILY_API_KEY")

        if not self.google_search_api_key:
            self.google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")

        if not self.google_search_engine_id:
            self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

        if not self.bing_search_api_key:
            self.bing_search_api_key = os.getenv("BING_SEARCH_API_KEY")

        if not self.serper_api_key:
            self.serper_api_key = os.getenv("SERPER_API_KEY")

        if not self.brave_search_api_key:
            self.brave_search_api_key = os.getenv("BRAVE_SEARCH_API_KEY")

        if not self.metasota_search_api_key:
            self.metasota_search_api_key = os.getenv("METASOSEARCH_API_KEY")

    def _auto_enable_sources(self):
        """自动启用有API密钥的源"""
        if self.newsapi_key:
            self.enable_newsapi = True

        if self.tavily_api_key:
            self.enable_tavily = True

        if self.google_search_api_key and self.google_search_engine_id:
            self.enable_google_search = True

        if self.bing_search_api_key:
            self.enable_bing_search = True

        if self.serper_api_key:
            self.enable_serper = True

        if self.brave_search_api_key:
            self.enable_brave_search = True

        if self.metasota_search_api_key:
            self.enable_metasota_search = True

    def get_enabled_sources(self) -> list:
        """获取启用的源列表"""
        sources = []

        if self.enable_hackernews:
            sources.append("hackernews")

        if self.enable_arxiv:
            sources.append("arxiv")

        if self.enable_newsapi and self.newsapi_key:
            sources.append("newsapi")

        if self.enable_rss_feeds:
            sources.append("rss")

        if self.enable_duckduckgo:
            sources.append("duckduckgo")

        if self.enable_tavily and self.tavily_api_key:
            sources.append("tavily")

        if self.enable_google_search and self.google_search_api_key:
            sources.append("google_search")

        if self.enable_bing_search and self.bing_search_api_key:
            sources.append("bing_search")

        if self.enable_serper and self.serper_api_key:
            sources.append("serper")

        if self.enable_brave_search and self.brave_search_api_key:
            sources.append("brave_search")

        if self.enable_metasota_search and self.metasota_search_api_key:
            sources.append("metasota_search")

        return sources

    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "enabled_sources": self.get_enabled_sources(),
        }

        # 检查是否有启用的源
        if not validation_result["enabled_sources"]:
            validation_result["valid"] = False
            validation_result["errors"].append("没有启用的搜索源")

        # 检查API密钥
        if self.enable_newsapi and not self.newsapi_key:
            validation_result["warnings"].append("NewsAPI已启用但缺少API密钥")

        if self.enable_tavily and not self.tavily_api_key:
            validation_result["warnings"].append("Tavily已启用但缺少API密钥")

        if self.enable_google_search and not self.google_search_api_key:
            validation_result["warnings"].append("Google搜索已启用但缺少API密钥")

        if self.enable_bing_search and not self.bing_search_api_key:
            validation_result["warnings"].append("Bing搜索已启用但缺少API密钥")

        if self.enable_serper and not self.serper_api_key:
            validation_result["warnings"].append("Serper已启用但缺少API密钥")

        if self.enable_brave_search and not self.brave_search_api_key:
            validation_result["warnings"].append("Brave搜索已启用但缺少API密钥")

        if self.enable_metasota_search and not self.metasota_search_api_key:
            validation_result["warnings"].append("MetaSota搜索已启用但缺少API密钥")

        return validation_result


@dataclass
class AdvancedSearchConfig(SearchConfig):
    """高级搜索配置"""

    # 高级功能
    enable_content_extraction: bool = True
    enable_sentiment_analysis: bool = False
    enable_keyword_extraction: bool = False
    cache_results: bool = True
    cache_duration_hours: int = 24

    # LLM 查询增强配置
    enable_query_enhancement: bool = False  # 是否启用 LLM 查询增强
    llm_provider: str = "google-gemini"  # LLM 提供商（当前只支持 google-gemini）
    llm_model: str = "gemini-2.5-pro"  # LLM 模型名称
    llm_api_key: Optional[str] = None  # Google Gemini API 密钥
    query_enhancement_cache_ttl: int = 24 * 60 * 60  # 查询增强缓存 TTL（秒），默认 24 小时

    # 内容处理参数
    max_content_length: int = 5000
    keyword_count: int = 10

    def __post_init__(self):
        """初始化后处理"""
        super().__post_init__()

        # 从环境变量加载 LLM API 密钥
        if not self.llm_api_key:
            self.llm_api_key = os.getenv("GOOGLE_API_KEY")

        # 验证高级配置
        if self.cache_duration_hours <= 0:
            self.cache_duration_hours = 24

        if self.max_content_length <= 0:
            self.max_content_length = 5000

        if self.keyword_count <= 0:
            self.keyword_count = 10

        if self.query_enhancement_cache_ttl <= 0:
            self.query_enhancement_cache_ttl = 24 * 60 * 60

    def get_advanced_features(self) -> Dict[str, bool]:
        """获取高级功能状态"""
        return {
            "content_extraction": self.enable_content_extraction,
            "sentiment_analysis": self.enable_sentiment_analysis,
            "keyword_extraction": self.enable_keyword_extraction,
            "caching": self.cache_results,
            "query_enhancement": self.enable_query_enhancement,
        }
