"""
灵活收集器
支持单个搜索引擎选择和独立参数设置
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable, Union
from difflib import SequenceMatcher

from ..models.article import Article
from ..models.result import SearchResult
from ..config.flexible_config import FlexibleSearchConfig, TimeRange
from ..tools.search_tools import (
    HackerNewsTool,
    ArxivTool,
    DuckDuckGoTool,
    NewsAPITool,
    TavilyTool,
    GoogleSearchTool,
    SerperTool,
    BraveSearchTool,
    MetaSotaSearchTool,
)

logger = logging.getLogger(__name__)


class FlexibleAINewsCollector:
    """灵活的AI新闻收集器"""
    
    def __init__(self, config: FlexibleSearchConfig):
        """
        初始化收集器
        
        Args:
            config: 灵活搜索配置
        """
        self.config = config
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """初始化搜索工具"""
        for engine_name, engine_config in self.config.engines.items():
            if not engine_config.enabled:
                continue
                
            try:
                tool = self._create_tool(engine_name, engine_config)
                if tool:
                    self.tools[engine_name] = tool
                    logger.info(f"初始化搜索引擎: {engine_name}")
            except Exception as e:
                logger.error(f"初始化搜索引擎 {engine_name} 失败: {e}")
    
    def _create_tool(self, engine_name: str, engine_config) -> Optional[Any]:
        """创建搜索工具"""
        max_articles = engine_config.max_articles
        
        if engine_name == "hackernews":
            return HackerNewsTool(max_articles=max_articles)
        elif engine_name == "arxiv":
            return ArxivTool(max_articles=max_articles)
        elif engine_name == "duckduckgo":
            return DuckDuckGoTool(max_articles=max_articles)
        elif engine_name == "rss_feeds":
            # 注意：这里需要根据实际的RSS工具类来调整
            return None  # 暂时返回None，需要实现RSS工具
        elif engine_name == "newsapi" and engine_config.api_key:
            return NewsAPITool(api_key=engine_config.api_key, max_articles=max_articles)
        elif engine_name == "tavily" and engine_config.api_key:
            return TavilyTool(api_key=engine_config.api_key, max_articles=max_articles)
        elif engine_name == "google_search" and engine_config.api_key:
            # 需要Google Search Engine ID，这里需要从配置中获取
            google_engine_id = getattr(self.config, 'google_search_engine_id', None)
            if google_engine_id:
                return GoogleSearchTool(
                    api_key=engine_config.api_key,
                    search_engine_id=google_engine_id,
                    max_articles=max_articles
                )
        elif engine_name == "bing_search" and engine_config.api_key:
            return BraveSearchTool(api_key=engine_config.api_key, max_articles=max_articles)
        elif engine_name == "serper" and engine_config.api_key:
            return SerperTool(api_key=engine_config.api_key, max_articles=max_articles)
        elif engine_name == "brave_search" and engine_config.api_key:
            return BraveSearchTool(api_key=engine_config.api_key, max_articles=max_articles)
        elif engine_name == "metasota_search" and engine_config.api_key:
            return MetaSotaSearchTool(api_key=engine_config.api_key, max_articles=max_articles)
        
        return None
    
    def _deduplicate_articles(self, articles: List[Article], similarity_threshold: float = None) -> List[Article]:
        """去重文章"""
        if similarity_threshold is None:
            similarity_threshold = self.config.global_similarity_threshold
            
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            is_duplicate = False
            for seen_title in seen_titles:
                similarity = SequenceMatcher(
                    None, article.title.lower(), seen_title.lower()
                ).ratio()
                if similarity > similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(article.title)
        
        return unique_articles
    
    async def collect_news(
        self,
        query: str = "artificial intelligence",
        engines: Optional[List[str]] = None,
        progress_callback: Optional[Callable] = None,
    ) -> SearchResult:
        """
        收集新闻
        
        Args:
            query: 搜索查询
            engines: 指定搜索引擎列表，None表示使用所有启用的引擎
            progress_callback: 进度回调函数
        
        Returns:
            SearchResult: 搜索结果
        """
        if engines is None:
            engines = list(self.tools.keys())
        
        all_articles = []
        source_progress = {}
        
        # 为所有引擎创建搜索任务
        tasks = {}
        for engine_name in engines:
            if engine_name in self.tools:
                engine_config = self.config.get_engine_config(engine_name)
                if engine_config:
                    task = self._search_single_engine(
                        engine_name, 
                        query, 
                        engine_config, 
                        progress_callback
                    )
                    tasks[engine_name] = task
                    source_progress[engine_name] = {"status": "pending", "articles_found": 0}
        
        # 并发执行所有搜索任务
        if tasks:
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            for engine_name, result in zip(tasks.keys(), results):
                try:
                    if isinstance(result, Exception):
                        logger.error(f"搜索失败 {engine_name}: {result}")
                        source_progress[engine_name] = {
                            "status": "failed",
                            "articles_found": 0,
                            "error": str(result),
                        }
                    else:
                        articles = result
                        all_articles.extend(articles)
                        source_progress[engine_name] = {
                            "status": "completed",
                            "articles_found": len(articles),
                        }
                        if progress_callback:
                            msg = f"完成 {engine_name}: {len(articles)} 篇文章"
                            progress_callback(msg)
                except Exception as e:
                    logger.error(f"处理搜索结果失败 {engine_name}: {e}")
                    source_progress[engine_name] = {
                        "status": "failed",
                        "articles_found": 0,
                        "error": str(e),
                    }
        
        # 去重
        unique_articles = self._deduplicate_articles(all_articles)
        
        return SearchResult(
            total_articles=len(all_articles),
            unique_articles=len(unique_articles),
            duplicates_removed=len(all_articles) - len(unique_articles),
            articles=unique_articles,
            source_progress=source_progress,
        )
    
    async def _search_single_engine(
        self, 
        engine_name: str, 
        query: str, 
        engine_config, 
        progress_callback: Optional[Callable] = None
    ):
        """搜索单个引擎"""
        if progress_callback:
            progress_callback(f"搜索 {engine_name}...")
        
        tool = self.tools[engine_name]
        # 使用引擎特定的时间范围
        days_back = engine_config.get_effective_days_back()
        
        # 将同步的搜索调用转移到线程池，避免阻塞事件循环
        articles = await asyncio.to_thread(tool.search, query, days_back)
        
        return articles
    
    def get_available_engines(self) -> List[str]:
        """获取可用的搜索引擎"""
        return list(self.tools.keys())
    
    def get_engine_info(self) -> Dict[str, Dict[str, Any]]:
        """获取搜索引擎信息"""
        engine_info = {}
        
        for engine_name, tool in self.tools.items():
            engine_config = self.config.get_engine_config(engine_name)
            engine_info[engine_name] = {
                "name": tool.__class__.__name__,
                "description": getattr(tool, "description", ""),
                "max_articles": getattr(tool, "max_articles", 0),
                "time_range": engine_config.time_range.value if engine_config else "unknown",
                "days_back": engine_config.get_effective_days_back() if engine_config else 0,
                "similarity_threshold": engine_config.similarity_threshold if engine_config else 0.85,
            }
        
        return engine_info
    
    def update_engine_config(
        self, 
        engine_name: str, 
        **kwargs
    ) -> bool:
        """更新搜索引擎配置"""
        if engine_name not in self.config.engines:
            return False
        
        self.config.set_engine_config(engine_name, **kwargs)
        
        # 如果配置了新的API密钥或启用了引擎，重新初始化工具
        if kwargs.get('enabled', False) or kwargs.get('api_key'):
            try:
                engine_config = self.config.get_engine_config(engine_name)
                if engine_config and engine_config.enabled:
                    tool = self._create_tool(engine_name, engine_config)
                    if tool:
                        self.tools[engine_name] = tool
                        logger.info(f"更新搜索引擎: {engine_name}")
                        return True
            except Exception as e:
                logger.error(f"更新搜索引擎 {engine_name} 失败: {e}")
                return False
        
        return True
    
    def set_time_range_for_engine(
        self, 
        engine_name: str, 
        time_range: TimeRange, 
        custom_days: Optional[int] = None
    ) -> bool:
        """为指定搜索引擎设置时间范围"""
        if engine_name not in self.config.engines:
            return False
        
        self.config.set_engine_time_range(engine_name, time_range, custom_days)
        return True
    
    def set_time_range_for_all_engines(self, time_range: TimeRange) -> None:
        """为所有搜索引擎设置统一的时间范围"""
        self.config.set_time_range_preset(time_range)


# 便捷函数
async def collect_with_single_engine(
    engine_name: str,
    query: str,
    time_range: TimeRange = TimeRange.ONE_WEEK,
    max_articles: int = 10,
    api_key: Optional[str] = None
) -> SearchResult:
    """
    使用单个搜索引擎收集新闻
    
    Args:
        engine_name: 搜索引擎名称
        query: 搜索查询
        time_range: 时间范围
        max_articles: 最大文章数
        api_key: API密钥（可选）
    
    Returns:
        SearchResult: 搜索结果
    """
    from ..config.flexible_config import create_single_engine_config
    
    config = create_single_engine_config(
        engine_name=engine_name,
        time_range=time_range,
        max_articles=max_articles,
        api_key=api_key
    )
    
    collector = FlexibleAINewsCollector(config)
    return await collector.collect_news(query)


async def collect_with_multiple_engines(
    engine_names: List[str],
    query: str,
    time_range: TimeRange = TimeRange.ONE_WEEK,
    max_articles_per_engine: int = 10
) -> SearchResult:
    """
    使用多个搜索引擎收集新闻
    
    Args:
        engine_names: 搜索引擎名称列表
        query: 搜索查询
        time_range: 时间范围
        max_articles_per_engine: 每个引擎的最大文章数
    
    Returns:
        SearchResult: 搜索结果
    """
    from ..config.flexible_config import create_flexible_config
    
    config = create_flexible_config(
        enabled_engines=engine_names,
        time_range=time_range,
        max_articles_per_engine=max_articles_per_engine
    )
    
    collector = FlexibleAINewsCollector(config)
    return await collector.collect_news(query)
