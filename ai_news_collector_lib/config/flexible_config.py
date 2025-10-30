"""
灵活配置模块
支持单个搜索引擎的独立配置和时间范围设置
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class TimeRange(Enum):
    """预设时间范围选项"""
    ONE_DAY = "1d"
    ONE_WEEK = "7d" 
    ONE_MONTH = "30d"
    ONE_YEAR = "365d"
    CUSTOM = "custom"


@dataclass
class EngineConfig:
    """单个搜索引擎的配置"""
    
    # 基础设置
    enabled: bool = True
    max_articles: int = 10
    days_back: int = 7
    similarity_threshold: float = 0.85
    
    # 时间范围设置
    time_range: TimeRange = TimeRange.ONE_WEEK
    custom_days: Optional[int] = None  # 当time_range为CUSTOM时使用
    
    # API密钥（可选）
    api_key: Optional[str] = None
    
    def get_effective_days_back(self) -> int:
        """获取有效的时间范围天数"""
        if self.time_range == TimeRange.CUSTOM and self.custom_days is not None:
            return self.custom_days
        elif self.time_range == TimeRange.ONE_DAY:
            return 1
        elif self.time_range == TimeRange.ONE_WEEK:
            return 7
        elif self.time_range == TimeRange.ONE_MONTH:
            return 30
        elif self.time_range == TimeRange.ONE_YEAR:
            return 365
        else:
            return self.days_back


@dataclass
class FlexibleSearchConfig:
    """灵活的搜索配置"""
    
    # 搜索引擎配置
    engines: Dict[str, EngineConfig] = field(default_factory=dict)
    
    # 全局设置
    global_similarity_threshold: float = 0.85
    global_max_articles: int = 10
    global_days_back: int = 7
    
    # 高级功能
    enable_content_extraction: bool = False
    enable_keyword_extraction: bool = False
    enable_sentiment_analysis: bool = False
    cache_results: bool = False
    cache_duration_hours: int = 24
    
    # LLM 查询增强配置
    enable_query_enhancement: bool = False
    llm_provider: str = "google-gemini"
    llm_model: str = "gemini-2.5-pro"
    llm_api_key: Optional[str] = None
    query_enhancement_cache_ttl: int = 24 * 60 * 60
    
    def __post_init__(self):
        """初始化后处理"""
        # 从环境变量加载LLM API密钥
        if not self.llm_api_key:
            self.llm_api_key = os.getenv("GOOGLE_API_KEY")
        
        # 初始化默认搜索引擎配置
        self._initialize_default_engines()
        
        # 从环境变量加载API密钥
        self._load_api_keys_from_env()
    
    def _initialize_default_engines(self):
        """初始化默认搜索引擎配置"""
        if not self.engines:
            # 免费搜索引擎
            self.engines["hackernews"] = EngineConfig(enabled=True)
            self.engines["arxiv"] = EngineConfig(enabled=True)
            self.engines["duckduckgo"] = EngineConfig(enabled=True)
            self.engines["rss_feeds"] = EngineConfig(enabled=True)
            
            # 付费搜索引擎（默认禁用）
            self.engines["newsapi"] = EngineConfig(enabled=False)
            self.engines["tavily"] = EngineConfig(enabled=False)
            self.engines["google_search"] = EngineConfig(enabled=False)
            self.engines["bing_search"] = EngineConfig(enabled=False)
            self.engines["serper"] = EngineConfig(enabled=False)
            self.engines["brave_search"] = EngineConfig(enabled=False)
            self.engines["metasota_search"] = EngineConfig(enabled=False)
    
    def _load_api_keys_from_env(self):
        """从环境变量加载API密钥"""
        api_key_mapping = {
            "newsapi": "NEWS_API_KEY",
            "tavily": "TAVILY_API_KEY", 
            "google_search": "GOOGLE_SEARCH_API_KEY",
            "bing_search": "BING_SEARCH_API_KEY",
            "serper": "SERPER_API_KEY",
            "brave_search": "BRAVE_SEARCH_API_KEY",
            "metasota_search": "METASOSEARCH_API_KEY",
        }
        
        for engine_name, env_var in api_key_mapping.items():
            if engine_name in self.engines:
                api_key = os.getenv(env_var)
                if api_key:
                    self.engines[engine_name].api_key = api_key
                    # 如果有API密钥，自动启用该搜索引擎
                    if not self.engines[engine_name].enabled:
                        self.engines[engine_name].enabled = True
    
    def set_engine_config(
        self, 
        engine_name: str, 
        enabled: bool = True,
        max_articles: Optional[int] = None,
        days_back: Optional[int] = None,
        time_range: Optional[TimeRange] = None,
        custom_days: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        api_key: Optional[str] = None
    ) -> None:
        """设置单个搜索引擎的配置"""
        if engine_name not in self.engines:
            self.engines[engine_name] = EngineConfig()
        
        engine_config = self.engines[engine_name]
        engine_config.enabled = enabled
        
        if max_articles is not None:
            engine_config.max_articles = max_articles
        if days_back is not None:
            engine_config.days_back = days_back
        if time_range is not None:
            engine_config.time_range = time_range
        if custom_days is not None:
            engine_config.custom_days = custom_days
        if similarity_threshold is not None:
            engine_config.similarity_threshold = similarity_threshold
        if api_key is not None:
            engine_config.api_key = api_key
    
    def get_enabled_engines(self) -> List[str]:
        """获取启用的搜索引擎列表"""
        return [name for name, config in self.engines.items() if config.enabled]
    
    def get_engine_config(self, engine_name: str) -> Optional[EngineConfig]:
        """获取指定搜索引擎的配置"""
        return self.engines.get(engine_name)
    
    def set_time_range_preset(self, time_range: TimeRange) -> None:
        """为所有搜索引擎设置统一的时间范围预设"""
        for engine_config in self.engines.values():
            engine_config.time_range = time_range
    
    def set_engine_time_range(self, engine_name: str, time_range: TimeRange, custom_days: Optional[int] = None) -> None:
        """为指定搜索引擎设置时间范围"""
        if engine_name in self.engines:
            self.engines[engine_name].time_range = time_range
            if custom_days is not None:
                self.engines[engine_name].custom_days = custom_days
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "enabled_engines": self.get_enabled_engines(),
            "engine_count": len(self.get_enabled_engines())
        }
        
        # 检查启用的搜索引擎
        if not validation_result["enabled_engines"]:
            validation_result["valid"] = False
            validation_result["errors"].append("没有启用任何搜索引擎")
        
        # 检查API密钥
        for engine_name, config in self.engines.items():
            if config.enabled and config.api_key is None:
                if engine_name in ["newsapi", "tavily", "google_search", "bing_search", "serper", "brave_search", "metasota_search"]:
                    validation_result["warnings"].append(f"{engine_name} 已启用但缺少API密钥")
        
        return validation_result
    
    def to_legacy_config(self) -> 'SearchConfig':
        """转换为传统的SearchConfig格式（向后兼容）"""
        from .settings import SearchConfig
        
        # 创建传统配置
        legacy_config = SearchConfig()
        
        # 设置搜索引擎启用状态
        for engine_name, config in self.engines.items():
            if config.enabled:
                if hasattr(legacy_config, f"enable_{engine_name}"):
                    setattr(legacy_config, f"enable_{engine_name}", True)
                if config.api_key and hasattr(legacy_config, f"{engine_name}_key"):
                    setattr(legacy_config, f"{engine_name}_key", config.api_key)
        
        # 设置全局参数
        legacy_config.max_articles_per_source = self.global_max_articles
        legacy_config.days_back = self.global_days_back
        legacy_config.similarity_threshold = self.global_similarity_threshold
        
        return legacy_config


# 便捷的配置创建函数
def create_flexible_config(
    enabled_engines: Optional[List[str]] = None,
    time_range: TimeRange = TimeRange.ONE_WEEK,
    max_articles_per_engine: int = 10
) -> FlexibleSearchConfig:
    """
    创建灵活的搜索配置
    
    Args:
        enabled_engines: 启用的搜索引擎列表，None表示使用默认
        time_range: 时间范围预设
        max_articles_per_engine: 每个搜索引擎的最大文章数
    
    Returns:
        FlexibleSearchConfig: 配置对象
    """
    config = FlexibleSearchConfig()
    
    # 设置时间范围
    config.set_time_range_preset(time_range)
    
    # 设置启用的搜索引擎
    if enabled_engines:
        # 先禁用所有搜索引擎
        for engine_config in config.engines.values():
            engine_config.enabled = False
        
        # 启用指定的搜索引擎
        for engine_name in enabled_engines:
            if engine_name in config.engines:
                config.set_engine_config(
                    engine_name, 
                    enabled=True, 
                    max_articles=max_articles_per_engine
                )
    
    return config


def create_single_engine_config(
    engine_name: str,
    time_range: TimeRange = TimeRange.ONE_WEEK,
    max_articles: int = 10,
    api_key: Optional[str] = None
) -> FlexibleSearchConfig:
    """
    创建单搜索引擎配置
    
    Args:
        engine_name: 搜索引擎名称
        time_range: 时间范围预设
        max_articles: 最大文章数
        api_key: API密钥（可选）
    
    Returns:
        FlexibleSearchConfig: 配置对象
    """
    config = FlexibleSearchConfig()
    
    # 禁用所有搜索引擎
    for engine_config in config.engines.values():
        engine_config.enabled = False
    
    # 启用指定的搜索引擎
    config.set_engine_config(
        engine_name,
        enabled=True,
        max_articles=max_articles,
        time_range=time_range,
        api_key=api_key
    )
    
    return config
