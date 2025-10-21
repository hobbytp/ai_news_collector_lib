"""
基础AI新闻搜集器
提供核心的新闻收集功能
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from difflib import SequenceMatcher

from ..models.article import Article
from ..models.result import SearchResult
from ..tools.search_tools import (
    HackerNewsTool, ArxivTool, DuckDuckGoTool, NewsAPITool,
    TavilyTool, GoogleSearchTool, SerperTool, BraveSearchTool, MetaSotaSearchTool
)
from ..config.settings import SearchConfig

logger = logging.getLogger(__name__)


class AINewsCollector:
    """AI新闻搜集器主类"""

    def __init__(self, config: SearchConfig):
        """
        初始化搜集器

        Args:
            config: 搜索配置
        """
        self.config = config
        self.tools = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """初始化搜索工具"""
        if self.config.enable_hackernews:
            self.tools['hackernews'] = HackerNewsTool(
                max_articles=self.config.max_articles_per_source
            )

        if self.config.enable_arxiv:
            self.tools['arxiv'] = ArxivTool(
                max_articles=self.config.max_articles_per_source
            )

        if self.config.enable_duckduckgo:
            self.tools['duckduckgo'] = DuckDuckGoTool(
                max_articles=self.config.max_articles_per_source
            )

        if self.config.enable_newsapi and self.config.newsapi_key:
            self.tools['newsapi'] = NewsAPITool(
                api_key=self.config.newsapi_key,
                max_articles=self.config.max_articles_per_source
            )

        if self.config.enable_tavily and self.config.tavily_api_key:
            self.tools['tavily'] = TavilyTool(
                api_key=self.config.tavily_api_key,
                max_articles=self.config.max_articles_per_source
            )

        google_enabled = (
            self.config.enable_google_search
            and self.config.google_search_api_key
            and self.config.google_search_engine_id
        )
        if google_enabled:
            self.tools['google_search'] = GoogleSearchTool(
                api_key=self.config.google_search_api_key,
                search_engine_id=self.config.google_search_engine_id,
                max_articles=self.config.max_articles_per_source
            )

        if self.config.enable_serper and self.config.serper_api_key:
            self.tools['serper'] = SerperTool(
                api_key=self.config.serper_api_key,
                max_articles=self.config.max_articles_per_source
            )

        brave_enabled = (
            self.config.enable_brave_search
            and self.config.brave_search_api_key
        )
        if brave_enabled:
            self.tools['brave_search'] = BraveSearchTool(
                api_key=self.config.brave_search_api_key,
                max_articles=self.config.max_articles_per_source
            )

        metasota_enabled = (
            self.config.enable_metasota_search
            and self.config.metasota_search_api_key
        )
        if metasota_enabled:
            self.tools['metasota_search'] = MetaSotaSearchTool(
                api_key=self.config.metasota_search_api_key,
                max_articles=self.config.max_articles_per_source
            )

        logger.info(f"初始化了 {len(self.tools)} 个搜索工具")

    def _deduplicate_articles(
        self, articles: List[Article]
    ) -> List[Article]:
        """去重文章"""
        unique_articles = []
        seen_titles = set()

        for article in articles:
            # 使用标题相似度去重
            is_duplicate = False
            for seen_title in seen_titles:
                similarity = SequenceMatcher(
                    None,
                    article.title.lower(),
                    seen_title.lower()
                ).ratio()
                if similarity > self.config.similarity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(article.title)

        return unique_articles

    async def collect_news(
        self,
        query: str = "artificial intelligence",
        sources: Optional[List[str]] = None,
        progress_callback: Optional[Callable] = None
    ) -> SearchResult:
        """
        收集AI新闻

        Args:
            query: 搜索查询
            sources: 指定搜索源列表
            progress_callback: 进度回调函数

        Returns:
            SearchResult: 搜索结果
        """
        if sources is None:
            sources = list(self.tools.keys())

        all_articles = []
        source_progress = {}

        # 为所有源创建搜索任务
        tasks = {}
        for source in sources:
            if source in self.tools:
                task = self._search_single_source(
                    source, query, progress_callback
                )
                tasks[source] = task
                source_progress[source] = {
                    'status': 'pending',
                    'articles_found': 0
                }

        # 并发执行所有搜索任务
        if tasks:
            results = await asyncio.gather(
                *tasks.values(), return_exceptions=True
            )

            for source, result in zip(tasks.keys(), results):
                try:
                    if isinstance(result, Exception):
                        logger.error(f"搜索失败 {source}: {result}")
                        source_progress[source] = {
                            'status': 'failed',
                            'articles_found': 0,
                            'error': str(result)
                        }
                    else:
                        articles = result
                        all_articles.extend(articles)
                        source_progress[source] = {
                            'status': 'completed',
                            'articles_found': len(articles)
                        }
                        if progress_callback:
                            msg = f"完成 {source}: {len(articles)} 篇文章"
                            progress_callback(msg)
                except Exception as e:
                    logger.error(f"处理搜索结果失败 {source}: {e}")
                    source_progress[source] = {
                        'status': 'failed',
                        'articles_found': 0,
                        'error': str(e)
                    }

        # 去重
        unique_articles = self._deduplicate_articles(all_articles)

        return SearchResult(
            total_articles=len(all_articles),
            unique_articles=len(unique_articles),
            duplicates_removed=len(all_articles) - len(unique_articles),
            articles=unique_articles,
            source_progress=source_progress
        )

    async def _search_single_source(
        self,
        source: str,
        query: str,
        progress_callback: Optional[Callable] = None
    ):
        """搜索单个源

        使用 asyncio.to_thread 将同步的搜索调用转移到线程池，
        避免阻塞事件循环
        """
        if progress_callback:
            progress_callback(f"搜索 {source}...")

        tool = self.tools[source]
        # 将同步的搜索调用转移到线程池，避免阻塞事件循环
        articles = await asyncio.to_thread(
            tool.search,
            query,
            self.config.days_back
        )

        return articles

    def get_available_sources(self) -> List[str]:
        """获取可用的搜索源"""
        return list(self.tools.keys())

    def get_source_info(self) -> Dict[str, Dict[str, Any]]:
        """获取搜索源信息"""
        source_info = {}

        for source, tool in self.tools.items():
            source_info[source] = {
                'name': tool.__class__.__name__,
                'description': getattr(tool, 'description', ''),
                'max_articles': getattr(tool, 'max_articles', 0)
            }

        return source_info
