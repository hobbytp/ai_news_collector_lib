"""
内容提取器
用于从网页中提取文章内容
"""

import requests
import logging
import re
from typing import Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ContentExtractor:
    """内容提取器"""
    
    def __init__(self, timeout: int = 10, max_length: int = 5000):
        """
        初始化内容提取器
        
        Args:
            timeout: 请求超时时间（秒）
            max_length: 最大内容长度
        """
        self.timeout = timeout
        self.max_length = max_length
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_content(self, url: str) -> str:
        """
        提取网页内容
        
        Args:
            url: 网页URL
            
        Returns:
            str: 提取的内容
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # 提取主要内容
            content = self._extract_main_content(soup)
            
            # 清理和格式化内容
            content = self._clean_content(content)
            
            # 限制长度
            if len(content) > self.max_length:
                content = content[:self.max_length] + "..."
            
            return content
            
        except Exception as e:
            logger.warning(f"Content extraction failed for {url}: {e}")
            return ""
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """提取主要内容"""
        # 尝试找到文章内容的选择器
        article_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'main',
            '.main-content',
            '#content',
            '.article-body',
            '.post-body'
        ]
        
        for selector in article_selectors:
            article_element = soup.select_one(selector)
            if article_element:
                content = article_element.get_text(strip=True)
                if len(content) > 200:  # 确保有足够的内容
                    return content
        
        # 如果没有找到特定容器，尝试从body中提取
        body = soup.find('body')
        if body:
            # 移除导航、侧边栏等
            for unwanted in body.find_all(['nav', 'aside', 'footer', 'header', 'script', 'style']):
                unwanted.decompose()
            
            content = body.get_text(strip=True)
            if len(content) > 200:
                return content
        
        # 最后尝试获取所有文本
        return soup.get_text(strip=True)
    
    def _clean_content(self, content: str) -> str:
        """清理内容"""
        # 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content)
        
        # 移除常见的无用文本
        unwanted_patterns = [
            r'Advertisement',
            r'Subscribe to our newsletter',
            r'Follow us on',
            r'Share this article',
            r'Related articles',
            r'Read more',
            r'Continue reading',
            r'Show more',
            r'Load more'
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    def extract_metadata(self, url: str) -> dict:
        """
        提取网页元数据
        
        Args:
            url: 网页URL
            
        Returns:
            dict: 元数据
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            metadata = {
                'title': '',
                'description': '',
                'author': '',
                'published_date': '',
                'keywords': []
            }
            
            # 提取标题
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text(strip=True)
            
            # 提取描述
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag:
                metadata['description'] = desc_tag.get('content', '')
            
            # 提取作者
            author_tag = soup.find('meta', attrs={'name': 'author'})
            if author_tag:
                metadata['author'] = author_tag.get('content', '')
            
            # 提取发布日期
            date_tag = soup.find('meta', attrs={'property': 'article:published_time'})
            if date_tag:
                metadata['published_date'] = date_tag.get('content', '')
            
            # 提取关键词
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_tag:
                keywords_str = keywords_tag.get('content', '')
                metadata['keywords'] = [kw.strip() for kw in keywords_str.split(',')]
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Metadata extraction failed for {url}: {e}")
            return {}
