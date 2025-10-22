"""
搜索结果数据模型
定义搜索结果的数据结构
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

from .article import Article


@dataclass
class SearchResult:
    """搜索结果数据结构"""

    total_articles: int
    unique_articles: int
    duplicates_removed: int
    articles: List[Article]
    source_progress: Dict[str, Dict[str, Any]]

    def __post_init__(self):
        """初始化后处理"""
        # 验证数据一致性
        if self.total_articles < self.unique_articles:
            self.total_articles = self.unique_articles

        if self.duplicates_removed != self.total_articles - self.unique_articles:
            self.duplicates_removed = self.total_articles - self.unique_articles

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "total_articles": self.total_articles,
            "unique_articles": self.unique_articles,
            "duplicates_removed": self.duplicates_removed,
            "articles": [article.to_dict() for article in self.articles],
            "source_progress": self.source_progress,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SearchResult":
        """从字典创建实例"""
        articles = []
        for article_data in data.get("articles", []):
            articles.append(Article.from_dict(article_data))

        return cls(
            total_articles=data.get("total_articles", 0),
            unique_articles=data.get("unique_articles", 0),
            duplicates_removed=data.get("duplicates_removed", 0),
            articles=articles,
            source_progress=data.get("source_progress", {}),
        )

    def get_summary(self) -> Dict[str, Any]:
        """获取结果摘要"""
        return {
            "total_articles": self.total_articles,
            "unique_articles": self.unique_articles,
            "duplicates_removed": self.duplicates_removed,
            "sources_count": len(self.source_progress),
            "successful_sources": len(
                [s for s in self.source_progress.values() if s.get("status") == "completed"]
            ),
            "failed_sources": len(
                [s for s in self.source_progress.values() if s.get("status") == "failed"]
            ),
        }

    def get_articles_by_source(self, source: str) -> List[Article]:
        """获取指定源的文章"""
        return [article for article in self.articles if article.source == source]

    def get_recent_articles(self, days: int = 7) -> List[Article]:
        """获取最近的文章"""
        recent_articles = []
        for article in self.articles:
            try:
                if not article.published:
                    continue

                # 处理不同的时间格式
                published_str = article.published
                if published_str.endswith("Z"):
                    published_str = published_str[:-1] + "+00:00"

                published_time = datetime.fromisoformat(published_str)
                now = (
                    datetime.now(published_time.tzinfo) if published_time.tzinfo else datetime.now()
                )

                if (now - published_time).days <= days:
                    recent_articles.append(article)
            except (ValueError, TypeError):
                continue

        return recent_articles

    def get_top_articles(self, limit: int = 10) -> List[Article]:
        """获取前N篇文章"""
        return self.articles[:limit]

    def get_source_statistics(self) -> Dict[str, int]:
        """获取各源统计信息"""
        stats = {}
        for article in self.articles:
            source = article.source
            stats[source] = stats.get(source, 0) + 1
        return stats
