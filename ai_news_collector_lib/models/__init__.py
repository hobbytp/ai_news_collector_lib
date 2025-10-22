"""
数据模型
定义文章、搜索结果等数据结构
"""

from .article import Article, AdvancedArticle
from .result import SearchResult
from .enhanced_query import EnhancedQuery

__all__ = ["Article", "AdvancedArticle", "SearchResult", "EnhancedQuery"]
