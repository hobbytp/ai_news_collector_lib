"""
文章数据模型
定义基础文章和增强文章的数据结构
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Article:
    """基础文章数据结构"""
    title: str
    url: str
    summary: str
    published: str
    author: str
    source_name: str
    source: str
    content: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保published是ISO格式
        if self.published and not self.published.endswith('Z') and 'T' in self.published:
            try:
                # 尝试解析并重新格式化
                dt = datetime.fromisoformat(self.published.replace('Z', '+00:00'))
                self.published = dt.isoformat()
            except ValueError:
                # 如果解析失败，保持原样
                pass
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'title': self.title,
            'url': self.url,
            'summary': self.summary,
            'published': self.published,
            'author': self.author,
            'source_name': self.source_name,
            'source': self.source,
            'content': self.content
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        """从字典创建实例"""
        return cls(
            title=data.get('title', ''),
            url=data.get('url', ''),
            summary=data.get('summary', ''),
            published=data.get('published', ''),
            author=data.get('author', ''),
            source_name=data.get('source_name', ''),
            source=data.get('source', ''),
            content=data.get('content')
        )


@dataclass
class AdvancedArticle(Article):
    """增强文章数据结构"""
    keywords: List[str] = field(default_factory=list)
    sentiment: Optional[str] = None
    word_count: int = 0
    reading_time: int = 0  # 分钟
    hash_id: str = ""
    
    def __post_init__(self):
        """初始化后处理"""
        super().__post_init__()
        
        # 计算阅读时间（如果没有设置）
        if self.reading_time == 0 and self.word_count > 0:
            self.reading_time = max(1, self.word_count // 200)  # 假设每分钟200字
    
    def to_dict(self) -> dict:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'keywords': self.keywords,
            'sentiment': self.sentiment,
            'word_count': self.word_count,
            'reading_time': self.reading_time,
            'hash_id': self.hash_id
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AdvancedArticle':
        """从字典创建实例"""
        return cls(
            title=data.get('title', ''),
            url=data.get('url', ''),
            summary=data.get('summary', ''),
            published=data.get('published', ''),
            author=data.get('author', ''),
            source_name=data.get('source_name', ''),
            source=data.get('source', ''),
            content=data.get('content'),
            keywords=data.get('keywords', []),
            sentiment=data.get('sentiment'),
            word_count=data.get('word_count', 0),
            reading_time=data.get('reading_time', 0),
            hash_id=data.get('hash_id', '')
        )
    
    def get_reading_time_text(self) -> str:
        """获取阅读时间文本"""
        if self.reading_time <= 1:
            return "1分钟"
        elif self.reading_time < 60:
            return f"{self.reading_time}分钟"
        else:
            hours = self.reading_time // 60
            minutes = self.reading_time % 60
            if minutes == 0:
                return f"{hours}小时"
            else:
                return f"{hours}小时{minutes}分钟"
    
    def get_keywords_text(self, max_keywords: int = 5) -> str:
        """获取关键词文本"""
        if not self.keywords:
            return "无关键词"
        
        keywords_to_show = self.keywords[:max_keywords]
        return ", ".join(keywords_to_show)
    
    def is_recent(self, days: int = 7) -> bool:
        """检查是否为最近的文章"""
        try:
            if not self.published:
                return False
            
            # 处理不同的时间格式
            published_str = self.published
            if published_str.endswith('Z'):
                published_str = published_str[:-1] + '+00:00'
            
            published_time = datetime.fromisoformat(published_str)
            now = datetime.now(published_time.tzinfo) if published_time.tzinfo else datetime.now()
            
            return (now - published_time).days <= days
        except (ValueError, TypeError):
            return False
