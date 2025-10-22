"""
API密钥管理
处理各种搜索服务的API密钥配置和管理
"""

import os
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class APIKeyManager:
    """API密钥管理器"""

    # API密钥存储
    newsapi_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    google_search_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None
    bing_search_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    brave_search_api_key: Optional[str] = None
    metasota_search_api_key: Optional[str] = None

    def __post_init__(self):
        """初始化后处理"""
        self._load_from_env()

    def _load_from_env(self):
        """从环境变量加载API密钥"""
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

    def get_available_keys(self) -> Dict[str, bool]:
        """获取可用的API密钥状态"""
        return {
            "newsapi": bool(self.newsapi_key),
            "tavily": bool(self.tavily_api_key),
            "google_search": bool(self.google_search_api_key and self.google_search_engine_id),
            "bing_search": bool(self.bing_search_api_key),
            "serper": bool(self.serper_api_key),
            "brave_search": bool(self.brave_search_api_key),
            "metasota_search": bool(self.metasota_search_api_key),
        }

    def get_key(self, service: str) -> Optional[str]:
        """获取指定服务的API密钥"""
        key_mapping = {
            "newsapi": self.newsapi_key,
            "tavily": self.tavily_api_key,
            "google_search": self.google_search_api_key,
            "bing_search": self.bing_search_api_key,
            "serper": self.serper_api_key,
            "brave_search": self.brave_search_api_key,
            "metasota_search": self.metasota_search_api_key,
        }
        return key_mapping.get(service)

    def set_key(self, service: str, key: str):
        """设置指定服务的API密钥"""
        if service == "newsapi":
            self.newsapi_key = key
        elif service == "tavily":
            self.tavily_api_key = key
        elif service == "google_search":
            self.google_search_api_key = key
        elif service == "google_search_engine_id":
            self.google_search_engine_id = key
        elif service == "bing_search":
            self.bing_search_api_key = key
        elif service == "serper":
            self.serper_api_key = key
        elif service == "brave_search":
            self.brave_search_api_key = key
        elif service == "metasota_search":
            self.metasota_search_api_key = key
        else:
            raise ValueError(f"Unknown service: {service}")

    def validate_keys(self) -> Dict[str, Any]:
        """验证API密钥"""
        validation_result = {"valid": True, "errors": [], "warnings": [], "available_services": []}

        # 检查可用的服务
        available_keys = self.get_available_keys()
        validation_result["available_services"] = [
            service for service, available in available_keys.items() if available
        ]

        # 检查Google搜索需要两个密钥
        if self.google_search_api_key and not self.google_search_engine_id:
            validation_result["warnings"].append("Google搜索API密钥已设置但缺少搜索引擎ID")

        if self.google_search_engine_id and not self.google_search_api_key:
            validation_result["warnings"].append("Google搜索引擎ID已设置但缺少API密钥")

        # 检查是否有任何可用的服务
        if not validation_result["available_services"]:
            validation_result["warnings"].append("没有配置任何API密钥，只能使用免费源")

        return validation_result

    def get_service_info(self) -> Dict[str, Dict[str, Any]]:
        """获取服务信息"""
        return {
            "newsapi": {
                "name": "NewsAPI",
                "description": "新闻API服务",
                "url": "https://newsapi.org/",
                "has_key": bool(self.newsapi_key),
                "required": True,
            },
            "tavily": {
                "name": "Tavily Search",
                "description": "AI搜索API",
                "url": "https://tavily.com/",
                "has_key": bool(self.tavily_api_key),
                "required": True,
            },
            "google_search": {
                "name": "Google Custom Search",
                "description": "Google自定义搜索API",
                "url": "https://developers.google.com/custom-search/",
                "has_key": bool(self.google_search_api_key and self.google_search_engine_id),
                "required": True,
            },
            "bing_search": {
                "name": "Bing Search API",
                "description": "微软Bing搜索API",
                "url": "https://www.microsoft.com/en-us/bing/apis/bing-web-search-api",
                "has_key": bool(self.bing_search_api_key),
                "required": True,
            },
            "serper": {
                "name": "Serper API",
                "description": "Serper搜索API",
                "url": "https://serper.dev/",
                "has_key": bool(self.serper_api_key),
                "required": True,
            },
            "brave_search": {
                "name": "Brave Search API",
                "description": "Brave搜索API",
                "url": "https://brave.com/search/api/",
                "has_key": bool(self.brave_search_api_key),
                "required": True,
            },
            "metasota_search": {
                "name": "MetaSota Search",
                "description": "MetaSota搜索服务 (ModelScope)",
                "url": "https://www.modelscope.cn/mcp/servers/metasota/metaso-search",
                "has_key": bool(self.metasota_search_api_key),
                "required": True,
            },
        }
