"""
高级AI新闻搜集器
提供增强功能：内容提取、关键词分析、缓存等
"""

import asyncio
import logging
import hashlib
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from ..models.article import Article, AdvancedArticle
from ..models.result import SearchResult
from ..config.settings import AdvancedSearchConfig
from ..utils.content_extractor import ContentExtractor
from ..utils.keyword_extractor import KeywordExtractor
from ..utils.cache import CacheManager
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
        # 转换为基础配置
        from ..config.settings import SearchConfig
        base_config = SearchConfig(
            enable_hackernews=config.enable_hackernews,
            enable_arxiv=config.enable_arxiv,
            enable_duckduckgo=config.enable_duckduckgo,
            enable_newsapi=config.enable_newsapi,
            newsapi_key=config.newsapi_key,
            max_articles_per_source=config.max_articles_per_source,
            days_back=config.days_back,
            similarity_threshold=config.similarity_threshold
        )
        
        super().__init__(base_config)
        self.advanced_config = config
        
        # 初始化高级功能
        self.content_extractor = ContentExtractor() if config.enable_content_extraction else None
        self.keyword_extractor = KeywordExtractor() if config.enable_keyword_extraction else None
        self.cache_manager = CacheManager() if config.cache_results else None
    
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
            hash_id=hash_id
        )
    
    async def collect_news_advanced(self, 
                                  query: str = "artificial intelligence",
                                  sources: Optional[List[str]] = None,
                                  progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        高级新闻收集
        
        Args:
            query: 搜索查询
            sources: 指定搜索源列表
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 增强的搜索结果
        """
        # 检查缓存
        if self.cache_manager:
            cache_key = self._generate_cache_key(query, sources)
            cached_result = self.cache_manager.get_cached_result(cache_key)
            if cached_result:
                logger.info("使用缓存结果")
                return cached_result
        
        # 执行基础搜索
        result = await self.collect_news(query, sources, progress_callback)
        
        # 增强文章信息
        enhanced_articles = []
        for article in result.articles:
            enhanced_article = self._enhance_article(article)
            enhanced_articles.append(enhanced_article)
        
        # 构建增强结果
        enhanced_result = {
            'query': query,
            'sources_searched': sources or self.get_available_sources(),
            'total_articles': result.total_articles,
            'unique_articles': result.unique_articles,
            'duplicates_removed': result.duplicates_removed,
            'articles': [
                {
                    'title': article.title,
                    'url': article.url,
                    'summary': article.summary,
                    'published': article.published,
                    'author': article.author,
                    'source_name': article.source_name,
                    'source': article.source,
                    'content': article.content,
                    'keywords': article.keywords,
                    'word_count': article.word_count,
                    'reading_time': article.reading_time,
                    'hash_id': article.hash_id
                }
                for article in enhanced_articles
            ],
            'source_progress': result.source_progress,
            'collection_time': datetime.now().isoformat()
        }
        
        # 缓存结果
        if self.cache_manager:
            self.cache_manager.cache_result(cache_key, enhanced_result)
        
        return enhanced_result
    
    def _generate_cache_key(self, query: str, sources: Optional[List[str]]) -> str:
        """生成缓存键"""
        sources_str = '_'.join(sorted(sources)) if sources else '_'.join(sorted(self.get_available_sources()))
        cache_data = f"{query}_{sources_str}_{self.advanced_config.days_back}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    async def collect_multiple_topics(self, 
                                    topics: List[str],
                                    progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
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
                result = await self.collect_news_advanced(topic, progress_callback=progress_callback)
                all_articles.extend(result['articles'])
                topic_results[topic] = {
                    'total': result['total_articles'],
                    'unique': result['unique_articles'],
                    'duplicates': result['duplicates_removed']
                }
            except Exception as e:
                logger.error(f"主题 '{topic}' 收集失败: {e}")
                topic_results[topic] = {'error': str(e)}
        
        # 去重
        unique_articles = self._deduplicate_enhanced_articles(all_articles)
        
        # 统计信息
        total_words = sum(article.get('word_count', 0) for article in unique_articles)
        avg_reading_time = sum(article.get('reading_time', 0) for article in unique_articles) / len(unique_articles) if unique_articles else 0
        
        return {
            'topics_searched': topics,
            'topic_results': topic_results,
            'total_articles': len(all_articles),
            'unique_articles': len(unique_articles),
            'duplicates_removed': len(all_articles) - len(unique_articles),
            'total_words': total_words,
            'average_reading_time': round(avg_reading_time, 1),
            'articles': unique_articles,
            'collection_time': datetime.now().isoformat()
        }
    
    def _deduplicate_enhanced_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重增强文章"""
        seen = set()
        unique = []
        
        for article in articles:
            key = f"{article.get('title', '')}_{article.get('url', '')}"
            if key not in seen:
                seen.add(key)
                unique.append(article)
        
        return unique
