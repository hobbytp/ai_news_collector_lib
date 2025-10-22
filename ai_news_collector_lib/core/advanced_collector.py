"""
高级AI新闻搜集器
提供增强功能：内容提取、关键词分析、缓存等
"""

import logging
import hashlib
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from ..models.article import Article, AdvancedArticle
from ..config.settings import AdvancedSearchConfig
from ..utils.content_extractor import ContentExtractor
from ..utils.keyword_extractor import KeywordExtractor
from ..utils.cache import CacheManager
from ..utils.query_enhancer import QueryEnhancer
from .collector import AINewsCollector

logger = logging.getLogger(__name__)


class AdvancedAINewsCollector(AINewsCollector):
    """高级AI新闻搜集器"""

    def __init__(self, config: AdvancedSearchConfig):
        """
        初始化高级搜集器

        Args:
            config: 高级搜索配置
        """
        # 直接使用高级配置（AdvancedSearchConfig 继承自 SearchConfig）
        super().__init__(config)
        self.advanced_config = config

        # 初始化高级功能
        content_extraction = config.enable_content_extraction
        self.content_extractor = ContentExtractor() if content_extraction else None
        keyword_extraction = config.enable_keyword_extraction
        self.keyword_extractor = KeywordExtractor() if keyword_extraction else None
        self.cache_manager = CacheManager() if config.cache_results else None

        # 初始化 LLM 查询增强器
        self.query_enhancer = None
        if config.enable_query_enhancement:
            try:
                self.query_enhancer = QueryEnhancer(
                    api_key=config.llm_api_key,
                    provider=config.llm_provider,
                    model=config.llm_model,
                    cache_ttl=config.query_enhancement_cache_ttl,
                    enable_caching=True,
                )
                logger.info("QueryEnhancer 初始化成功")
            except Exception as e:
                logger.warning(f"QueryEnhancer 初始化失败: {e}。查询增强功能将被禁用。")

    def _enhance_article(self, article: Article) -> AdvancedArticle:
        """增强文章信息"""
        # 提取内容
        content = ""
        if self.content_extractor and article.url:
            content = self.content_extractor.extract_content(article.url)

        # 提取关键词
        keywords = []
        if self.keyword_extractor:
            text_for_keywords = f"{article.title} {article.summary} {content}"
            keywords = self.keyword_extractor.extract_keywords(text_for_keywords)

        # 计算字数
        word_count = len(content.split()) if content else 0

        # 计算阅读时间（假设每分钟200字）
        reading_time = max(1, word_count // 200)

        # 生成哈希ID
        hash_input = f"{article.title}_{article.url}_{article.published}"
        hash_id = hashlib.md5(hash_input.encode()).hexdigest()[:12]

        return AdvancedArticle(
            title=article.title,
            url=article.url,
            summary=article.summary,
            published=article.published,
            author=article.author,
            source_name=article.source_name,
            source=article.source,
            content=content,
            keywords=keywords,
            word_count=word_count,
            reading_time=reading_time,
            hash_id=hash_id,
        )

    async def collect_news_advanced(
        self,
        query: str = "artificial intelligence",
        sources: Optional[List[str]] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        高级新闻收集（支持 LLM 查询增强）

        Args:
            query: 搜索查询
            sources: 指定搜索源列表
            progress_callback: 进度回调函数

        Returns:
            Dict: 增强的搜索结果
        """
        # 存储 LLM 增强后的查询映射
        enhanced_queries: Dict[str, str] = {}

        # 步骤 1: LLM 查询增强（如果启用）
        if self.query_enhancer:
            try:
                # 确定启用的引擎
                enabled_engines = sources if sources else self.get_available_sources()

                # 调用 LLM 进行单一查询增强（生成所有启用引擎的变体）
                logger.info(f"使用 LLM 增强查询，启用引擎: {enabled_engines}")
                enhanced = self.query_enhancer.enhance_query(
                    original_query=query, enabled_engines=enabled_engines
                )

                # 存储增强后的查询映射
                for engine in enabled_engines:
                    engine_query = enhanced.get_for_engine(engine)
                    if engine_query:
                        enhanced_queries[engine] = engine_query

                logger.info(f"LLM 增强成功，生成 {len(enhanced_queries)} 个引擎的优化查询")

            except Exception as e:
                logger.warning(f"LLM 查询增强失败: {e}。使用原始查询继续。")

        # 检查缓存
        if self.cache_manager:
            cache_key = self._generate_cache_key(query, sources)
            cached_result = self.cache_manager.get_cached_result(cache_key)
            if cached_result:
                logger.info("使用缓存结果")
                return cached_result

        # 步骤 2: 执行基础搜索（使用增强查询或原始查询）
        # 注意: 这里使用原始查询进行搜索，因为搜索引擎会根据启用的源来选择使用增强查询
        result = await self.collect_news(query, sources, progress_callback)

        # 步骤 3: 增强文章信息
        enhanced_articles = []
        for article in result.articles:
            enhanced_article = self._enhance_article(article)
            enhanced_articles.append(enhanced_article)

        # 步骤 4: 构建增强结果
        available_sources = self.get_available_sources()
        enhanced_result = {
            "query": query,
            "enhanced_queries": enhanced_queries,  # 新增: LLM 优化的查询映射
            "sources_searched": sources or available_sources,
            "total_articles": result.total_articles,
            "unique_articles": result.unique_articles,
            "duplicates_removed": result.duplicates_removed,
            "articles": [
                {
                    "title": article.title,
                    "url": article.url,
                    "summary": article.summary,
                    "published": article.published,
                    "author": article.author,
                    "source_name": article.source_name,
                    "source": article.source,
                    "content": article.content,
                    "keywords": article.keywords,
                    "word_count": article.word_count,
                    "reading_time": article.reading_time,
                    "hash_id": article.hash_id,
                }
                for article in enhanced_articles
            ],
            "source_progress": result.source_progress,
            "collection_time": datetime.now().isoformat(),
            "query_enhancement_enabled": bool(self.query_enhancer),
        }

        # 步骤 5: 缓存结果
        if self.cache_manager:
            self.cache_manager.cache_result(cache_key, enhanced_result)

        return enhanced_result

    def _generate_cache_key(self, query: str, sources: Optional[List[str]]) -> str:
        """生成缓存键"""
        if sources:
            sources_str = "_".join(sorted(sources))
        else:
            available = self.get_available_sources()
            sources_str = "_".join(sorted(available))
        cache_data = f"{query}_{sources_str}_{self.advanced_config.days_back}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    async def collect_multiple_topics(
        self, topics: List[str], progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        收集多个主题的新闻

        Args:
            topics: 主题列表
            progress_callback: 进度回调函数

        Returns:
            Dict: 多主题搜索结果
        """
        all_articles = []
        topic_results = {}

        for topic in topics:
            if progress_callback:
                progress_callback(f"收集主题: {topic}")

            try:
                result = await self.collect_news_advanced(
                    topic, progress_callback=progress_callback
                )
                all_articles.extend(result["articles"])
                topic_results[topic] = {
                    "total": result["total_articles"],
                    "unique": result["unique_articles"],
                    "duplicates": result["duplicates_removed"],
                }
            except Exception as e:
                logger.error(f"主题 '{topic}' 收集失败: {e}")
                topic_results[topic] = {"error": str(e)}

        # 去重
        unique_articles = self._deduplicate_enhanced_articles(all_articles)

        # 统计信息
        total_words = sum(article.get("word_count", 0) for article in unique_articles)
        if unique_articles:
            total_reading = sum(article.get("reading_time", 0) for article in unique_articles)
            avg_reading_time = total_reading / len(unique_articles)
        else:
            avg_reading_time = 0

        return {
            "topics_searched": topics,
            "topic_results": topic_results,
            "total_articles": len(all_articles),
            "unique_articles": len(unique_articles),
            "duplicates_removed": len(all_articles) - len(unique_articles),
            "total_words": total_words,
            "average_reading_time": round(avg_reading_time, 1),
            "articles": unique_articles,
            "collection_time": datetime.now().isoformat(),
        }

    def _deduplicate_enhanced_articles(
        self, articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """去重增强文章"""
        seen = set()
        unique = []

        for article in articles:
            key = f"{article.get('title', '')}_{article.get('url', '')}"
            if key not in seen:
                seen.add(key)
                unique.append(article)

        return unique
