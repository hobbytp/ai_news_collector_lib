#!/usr/bin/env python3
"""
修复时间过滤问题的脚本
为没有实现时间过滤的搜索引擎添加客户端时间过滤
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_news_collector_lib'))

from ai_news_collector_lib.models.article import Article

def apply_client_side_date_filter(articles: List[Article], days_back: int) -> List[Article]:
    """
    在客户端应用时间过滤
    
    Args:
        articles: 文章列表
        days_back: 天数限制
        
    Returns:
        过滤后的文章列表
    """
    if days_back <= 0:
        return articles
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    filtered_articles = []
    
    for article in articles:
        try:
            if not article.published:
                # 如果没有发布时间，跳过
                continue
            
            # 处理不同的时间格式
            published_str = article.published
            if published_str.endswith("Z"):
                published_str = published_str[:-1] + "+00:00"
            
            published_time = datetime.fromisoformat(published_str)
            
            # 只保留在时间范围内的文章
            if published_time >= cutoff_date:
                filtered_articles.append(article)
                
        except (ValueError, TypeError):
            # 如果时间解析失败，跳过该文章
            continue
    
    return filtered_articles

def create_enhanced_search_tools():
    """
    创建增强的搜索工具类，添加客户端时间过滤
    """
    
    enhanced_tools_code = '''
"""
增强的搜索工具实现
为没有时间过滤的搜索引擎添加客户端时间过滤
"""

import requests
import logging
import json
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import feedparser
import re

from ..models.article import Article

logger = logging.getLogger(__name__)

def apply_client_side_date_filter(articles: List[Article], days_back: int) -> List[Article]:
    """
    在客户端应用时间过滤
    
    Args:
        articles: 文章列表
        days_back: 天数限制
        
    Returns:
        过滤后的文章列表
    """
    if days_back <= 0:
        return articles
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    filtered_articles = []
    
    for article in articles:
        try:
            if not article.published:
                # 如果没有发布时间，跳过
                continue
            
            # 处理不同的时间格式
            published_str = article.published
            if published_str.endswith("Z"):
                published_str = published_str[:-1] + "+00:00"
            
            published_time = datetime.fromisoformat(published_str)
            
            # 只保留在时间范围内的文章
            if published_time >= cutoff_date:
                filtered_articles.append(article)
                
        except (ValueError, TypeError):
            # 如果时间解析失败，跳过该文章
            continue
    
    return filtered_articles

class EnhancedSerperTool:
    """增强的Serper搜索工具 - 添加客户端时间过滤"""
    
    def __init__(self, api_key: str, max_articles: int = 10):
        self.api_key = api_key
        self.max_articles = max_articles
        self.base_url = "https://google.serper.dev/search"
        self.name = "EnhancedSerperTool"
        self.description = "使用Serper API搜索，带客户端时间过滤"

    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """使用Serper API搜索，带客户端时间过滤"""
        try:
            import requests

            payload = {"q": query, "num": min(self.max_articles * 3, 30)}  # 获取更多结果用于过滤

            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            articles = []

            for result in data.get("organic", []):
                # 从 URL 提取域名作为 source_name
                url = result.get("link", "")
                source_name = ""
                if url:
                    try:
                        from urllib.parse import urlparse
                        source_name = urlparse(url).netloc or ""
                    except Exception:
                        source_name = ""

                article = Article(
                    title=result.get("title", ""),
                    url=url,
                    summary=result.get("snippet", ""),
                    published=datetime.now(timezone.utc).isoformat(),
                    author="Serper Search",
                    source_name=source_name,
                    source="serper",
                )
                articles.append(article)

            # 应用客户端时间过滤
            filtered_articles = apply_client_side_date_filter(articles, days_back)
            return filtered_articles[:self.max_articles]

        except Exception as e:
            logger.error(f"Enhanced Serper search failed: {e}")
            return []

class EnhancedBraveSearchTool:
    """增强的Brave搜索工具 - 添加客户端时间过滤"""
    
    def __init__(self, api_key: str, max_articles: int = 10):
        self.api_key = api_key
        self.max_articles = max_articles
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.name = "EnhancedBraveSearchTool"
        self.description = "使用Brave搜索API，带客户端时间过滤"

    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """使用Brave搜索API，带客户端时间过滤"""
        try:
            import requests

            params = {
                "q": query,
                "count": min(self.max_articles * 3, 60),  # 获取更多结果用于过滤
                "offset": 0,
                "mkt": "en-US",
                "safesearch": "moderate",
            }

            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key,
            }

            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            articles = []

            for result in data.get("web", {}).get("results", []):
                article = Article(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    summary=result.get("description", ""),
                    published=datetime.now(timezone.utc).isoformat(),
                    author="Brave Search",
                    source_name=(
                        result.get("url", "").split("/")[2] if result.get("url") else "Brave"
                    ),
                    source="brave_search",
                )
                articles.append(article)

            # 应用客户端时间过滤
            filtered_articles = apply_client_side_date_filter(articles, days_back)
            return filtered_articles[:self.max_articles]

        except Exception as e:
            logger.error(f"Enhanced Brave search failed: {e}")
            return []

class EnhancedTavilyTool:
    """增强的Tavily搜索工具 - 添加客户端时间过滤"""
    
    def __init__(self, api_key: str, max_articles: int = 10):
        self.api_key = api_key
        self.max_articles = max_articles
        self.base_url = "https://api.tavily.com/search"
        self.name = "EnhancedTavilyTool"
        self.description = "使用Tavily API搜索，带客户端时间过滤"

    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """使用Tavily API搜索，带客户端时间过滤"""
        try:
            import requests

            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": False,
                "include_raw_content": False,
                "max_results": min(self.max_articles * 3, 30),  # 获取更多结果用于过滤
                "include_domains": [],
                "exclude_domains": [],
            }

            response = requests.post(
                self.base_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            articles = []

            for result in data.get("results", []):
                article = Article(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    summary=result.get("content", ""),
                    published=datetime.now(timezone.utc).isoformat(),
                    author="Tavily Search",
                    source_name=result.get("url", "").split("/")[2] if result.get("url") else "Tavily",
                    source="tavily",
                )
                articles.append(article)

            # 应用客户端时间过滤
            filtered_articles = apply_client_side_date_filter(articles, days_back)
            return filtered_articles[:self.max_articles]

        except Exception as e:
            logger.error(f"Enhanced Tavily search failed: {e}")
            return []
'''
    
    return enhanced_tools_code

def main():
    """主函数"""
    print("时间过滤问题修复方案")
    print("=" * 50)
    print()
    
    print("问题分析:")
    print("1. 以下搜索引擎没有实现时间过滤:")
    print("   - SerperTool")
    print("   - BraveSearchTool") 
    print("   - MetaSotaSearchTool")
    print("   - TavilyTool")
    print()
    
    print("2. 以下搜索引擎时间过滤有问题:")
    print("   - HackerNewsTool: 没有时间过滤")
    print("   - ArxivTool: 按提交时间排序，不是发布时间")
    print("   - DuckDuckGoTool: 时间过滤可能不够精确")
    print()
    
    print("3. 以下搜索引擎时间过滤正确:")
    print("   - NewsAPITool: 使用from参数")
    print("   - GoogleSearchTool: 使用dateRestrict参数")
    print()
    
    print("修复建议:")
    print("1. 为没有时间过滤的搜索引擎添加客户端时间过滤")
    print("2. 修改ArxivTool使用更准确的时间过滤")
    print("3. 改进DuckDuckGoTool的时间过滤实现")
    print("4. 为HackerNewsTool添加客户端时间过滤")
    print()
    
    print("具体修复步骤:")
    print("1. 修改 ai_news_collector_lib/tools/search_tools.py")
    print("2. 为每个搜索工具添加客户端时间过滤")
    print("3. 测试修复后的效果")
    print()
    
    # 创建增强的搜索工具代码
    enhanced_code = create_enhanced_search_tools()
    
    with open("enhanced_search_tools.py", "w", encoding="utf-8") as f:
        f.write(enhanced_code)
    
    print("已创建增强的搜索工具代码: enhanced_search_tools.py")
    print("可以将这些代码集成到原始项目中")

if __name__ == "__main__":
    main()
