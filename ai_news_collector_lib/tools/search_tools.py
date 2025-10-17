"""
搜索工具实现
包含各种搜索源的具体实现
"""

import requests
import logging
import json
from typing import List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import feedparser
import re

from ..models.article import Article

logger = logging.getLogger(__name__)


class BaseSearchTool:
    """搜索工具基类"""
    
    def __init__(self, max_articles: int = 10):
        self.max_articles = max_articles
        self.name = self.__class__.__name__
        self.description = f"搜索工具: {self.name}"
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            days_back: 搜索天数
            
        Returns:
            List[Article]: 文章列表
        """
        raise NotImplementedError("子类必须实现search方法")
    
    def _filter_by_date(self, articles: List[Article], days_back: int) -> List[Article]:
        """按日期过滤文章"""
        if days_back <= 0:
            return articles
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        filtered_articles = []
        
        for article in articles:
            try:
                if not article.published:
                    continue
                
                # 处理不同的时间格式
                published_str = article.published
                if published_str.endswith('Z'):
                    published_str = published_str[:-1] + '+00:00'
                
                published_time = datetime.fromisoformat(published_str)
                if published_time >= cutoff_date:
                    filtered_articles.append(article)
            except (ValueError, TypeError):
                # 如果时间解析失败，保留文章
                filtered_articles.append(article)
        
        return filtered_articles


class HackerNewsTool(BaseSearchTool):
    """HackerNews搜索工具"""
    
    def __init__(self, max_articles: int = 10):
        super().__init__(max_articles)
        self.description = "从HackerNews获取技术新闻和讨论"
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """搜索HackerNews"""
        try:
            # 获取最新文章
            response = requests.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json",
                timeout=10
            )
            response.raise_for_status()
            story_ids = response.json()[:50]  # 获取前50个故事
            
            articles = []
            for story_id in story_ids:
                try:
                    story_response = requests.get(
                        f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                        timeout=5
                    )
                    story_data = story_response.json()
                    
                    if story_data and story_data.get('type') == 'story':
                        story_time = datetime.fromtimestamp(story_data.get('time', 0))
                        
                        # 检查是否包含查询关键词
                        title = story_data.get('title', '').lower()
                        if any(keyword.lower() in title for keyword in query.split()):
                            article = Article(
                                title=story_data.get('title', 'No title'),
                                url=story_data.get('url', ''),
                                summary=f"Score: {story_data.get('score', 0)} | Comments: {story_data.get('descendants', 0)}",
                                published=story_time.isoformat(),
                                author=story_data.get('by', 'Unknown'),
                                source_name='HackerNews',
                                source='hackernews'
                            )
                            articles.append(article)
                            
                            if len(articles) >= self.max_articles:
                                break
                except Exception as e:
                    logger.warning(f"Error fetching HackerNews story {story_id}: {e}")
                    continue
            
            # 按日期过滤
            articles = self._filter_by_date(articles, days_back)
            return articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"HackerNews search failed: {e}")
            return []


class ArxivTool(BaseSearchTool):
    """ArXiv搜索工具"""
    
    def __init__(self, max_articles: int = 10):
        super().__init__(max_articles)
        self.description = "从ArXiv获取学术论文和预印本"
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """搜索ArXiv"""
        try:
            # 构建ArXiv搜索URL
            search_query = f"cat:cs.AI OR cat:cs.LG OR cat:cs.CL AND all:{query}"
            url = f"http://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results={self.max_articles}&sortBy=submittedDate&sortOrder=descending"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            articles: List[Article] = []
            
            # 优先使用BeautifulSoup的XML解析；失败时回退到feedparser
            try:
                soup = BeautifulSoup(response.content, 'xml')
                entries = soup.find_all('entry')
                
                for entry in entries:
                    try:
                        published_str = entry.find('published').text
                        published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                        
                        article = Article(
                            title=entry.find('title').text.strip(),
                            url=entry.find('id').text,
                            summary=entry.find('summary').text.strip()[:500] + '...',
                            published=published_date.isoformat(),
                            author=', '.join([author.find('name').text for author in entry.find_all('author')]),
                            source_name='ArXiv',
                            source='arxiv'
                        )
                        articles.append(article)
                        
                        if len(articles) >= self.max_articles:
                            break
                    except Exception as e:
                        logger.warning(f"Error parsing ArXiv entry: {e}")
                        continue
            except Exception as soup_error:
                logger.warning(f"BeautifulSoup XML解析失败，使用feedparser回退: {soup_error}")
                feed = feedparser.parse(response.content)
                for entry in feed.entries:
                    try:
                        # 解析发布时间
                        # 说明：feedparser 可能仅提供 published_parsed 或 updated_parsed，两者单位均为 time.struct_time
                        # 这里按优先级回退：published_parsed > updated_parsed > 当前时间
                        try:
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                published_date = datetime(*entry.published_parsed[:6])
                            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                                published_date = datetime(*entry.updated_parsed[:6])
                            else:
                                published_date = datetime.now()
                        except Exception:
                            published_date = datetime.now()
                        
                        article = Article(
                            title=getattr(entry, 'title', '').strip(),
                            url=getattr(entry, 'id', '') or getattr(entry, 'link', ''),
                            summary=(getattr(entry, 'summary', '') or getattr(entry, 'content', [{'value': ''}])[0].get('value', '')).strip()[:500] + '...',
                            published=published_date.isoformat(),
                            author=', '.join([a.get('name', '') for a in getattr(entry, 'authors', [])]) if hasattr(entry, 'authors') else 'ArXiv',
                            source_name='ArXiv',
                            source='arxiv'
                        )
                        articles.append(article)
                        if len(articles) >= self.max_articles:
                            break
                    except Exception as e:
                        logger.warning(f"Error parsing ArXiv feed entry: {e}")
                        continue
            
            # 按日期过滤
            articles = self._filter_by_date(articles, days_back)
            return articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"ArXiv search failed: {e}")
            return []


class DuckDuckGoTool(BaseSearchTool):
    """DuckDuckGo搜索工具"""
    
    def __init__(self, max_articles: int = 10):
        super().__init__(max_articles)
        self.description = "使用DuckDuckGo进行隐私保护的网页搜索"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """搜索DuckDuckGo"""
        try:
            # 添加时间过滤和站点限制
            time_filter = f" after:{(datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')}"
            search_query = f"{query} site:techcrunch.com OR site:venturebeat.com OR site:theverge.com OR site:wired.com{time_filter}"
            
            params = {
                'q': search_query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(
                "https://duckduckgo.com/",
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            # 解析搜索结果（简化版）
            articles = []
            soup = BeautifulSoup(response.text, 'html.parser')
            result_links = soup.find_all('a', href=True)
            
            for link in result_links:
                href = str(link.get('href', ''))
                title = link.get_text(strip=True)
                
                if (href and href.startswith('http') and
                    any(domain in href for domain in ['techcrunch.com', 'venturebeat.com', 'theverge.com', 'wired.com']) and
                    len(title) > 10):
                    
                    article = Article(
                        title=title,
                        url=href,
                        summary=f"AI news article found via DuckDuckGo search for '{query}'",
                        published=datetime.now().isoformat(),
                        author='DuckDuckGo Search',
                        source_name='DuckDuckGo',
                        source='duckduckgo'
                    )
                    articles.append(article)
                    
                    if len(articles) >= self.max_articles:
                        break
            
            return articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []


class NewsAPITool(BaseSearchTool):
    """NewsAPI搜索工具"""
    
    def __init__(self, api_key: str, max_articles: int = 10):
        super().__init__(max_articles)
        self.api_key = api_key
        self.description = "使用NewsAPI获取多源新闻"
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """搜索NewsAPI"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f"{query} AI artificial intelligence",
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': self.max_articles,
                'from': (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get('articles', []):
                if item.get('title') and item.get('url'):
                    article = Article(
                        title=item.get('title', 'No title'),
                        url=item.get('url', ''),
                        summary=item.get('description', 'No summary'),
                        published=item.get('publishedAt', datetime.now().isoformat()),
                        author=item.get('author', 'Unknown'),
                        source_name=item.get('source', {}).get('name', 'NewsAPI'),
                        source='newsapi'
                    )
                    articles.append(article)
            
            return articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"NewsAPI search failed: {e}")
            return []


class TavilyTool(BaseSearchTool):
    """Tavily搜索工具"""
    
    def __init__(self, api_key: str, max_articles: int = 10):
        super().__init__(max_articles)
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """使用Tavily API搜索"""
        try:
            import requests
            
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": False,
                "include_raw_content": False,
                "max_results": self.max_articles,
                "include_domains": [],
                "exclude_domains": []
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for result in data.get('results', []):
                # 检查日期过滤
                published_date = datetime.now()
                if result.get('published_date'):
                    try:
                        published_date = datetime.fromisoformat(result['published_date'].replace('Z', '+00:00'))
                    except:
                        pass
                
                if published_date >= start_date:
                    article = Article(
                        title=result.get('title', ''),
                        url=result.get('url', ''),
                        summary=result.get('content', ''),
                        published=published_date.isoformat(),
                        author='Tavily Search',
                        source_name=result.get('url', '').split('/')[2] if result.get('url') else 'Tavily',
                        source='tavily'
                    )
                    articles.append(article)
            
            return articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []


class GoogleSearchTool(BaseSearchTool):
    """Google自定义搜索工具"""
    
    def __init__(self, api_key: str, search_engine_id: str, max_articles: int = 10):
        super().__init__(max_articles)
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """使用Google自定义搜索API"""
        try:
            import requests
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(self.max_articles, 10),  # Google API限制
                'dateRestrict': f'd{days_back}',  # 限制天数
                'sort': 'date'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get('items', []):
                article = Article(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    summary=item.get('snippet', ''),
                    published=datetime.now().isoformat(),  # Google API不总是提供日期
                    author='Google Search',
                    source_name=item.get('displayLink', ''),
                    source='google_search'
                )
                articles.append(article)
            
            return articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []


class SerperTool(BaseSearchTool):
    """Serper搜索工具"""
    
    def __init__(self, api_key: str, max_articles: int = 10):
        super().__init__(max_articles)
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """使用Serper API搜索"""
        try:
            import requests
            
            payload = {
                "q": query,
                "num": min(self.max_articles, 10)
            }
            
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for result in data.get('organic', []):
                article = Article(
                    title=result.get('title', ''),
                    url=result.get('link', ''),
                    summary=result.get('snippet', ''),
                    published=datetime.now().isoformat(),
                    author='Serper Search',
                    source_name=result.get('displayLink', ''),
                    source='serper'
                )
                articles.append(article)
            
            return articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            return []


class BraveSearchTool(BaseSearchTool):
    """Brave搜索工具"""
    
    def __init__(self, api_key: str, max_articles: int = 10):
        super().__init__(max_articles)
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """使用Brave搜索API"""
        try:
            import requests
            
            params = {
                'q': query,
                'count': min(self.max_articles, 20),
                'offset': 0,
                'mkt': 'en-US',
                'safesearch': 'moderate'
            }
            
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'X-Subscription-Token': self.api_key
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for result in data.get('web', {}).get('results', []):
                article = Article(
                    title=result.get('title', ''),
                    url=result.get('url', ''),
                    summary=result.get('description', ''),
                    published=datetime.now().isoformat(),
                    author='Brave Search',
                    source_name=result.get('url', '').split('/')[2] if result.get('url') else 'Brave',
                    source='brave_search'
                )
                articles.append(article)
            
            return articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            return []


class MetaSotaSearchTool(BaseSearchTool):
    """
    MetaSota搜索工具 - 基于ModelScope MCP服务器的搜索服务
    参考：https://www.modelscope.cn/mcp/servers/metasota/metaso-search
    
    """
    
    def __init__(self, api_key: str, max_articles: int = 10):
        super().__init__(max_articles)
        self.api_key = api_key
        # 正确的MCP服务器端点
        self.mcp_base_url = "https://metaso.cn/api/mcp"
        self.is_available = False
        self._test_mcp_connection()
    
    def _test_mcp_connection(self):
        """测试MCP服务器连接"""
        try:
            import requests
            # 使用正确的认证头测试MCP服务器
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'AI-News-Collector/1.0',
                'Accept': 'application/json'
            }
            
            # 测试MCP服务器健康状态
            response = requests.get(self.mcp_base_url, headers=headers, timeout=10)
            if response.status_code == 200:
                # 检查响应是否为JSON
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    self.is_available = True
                    logger.info("MetaSota MCP服务器连接成功")
                else:
                    logger.warning("MetaSota MCP服务器返回非JSON响应")
            elif response.status_code == 401:
                logger.warning("MetaSota MCP服务器认证失败，请检查API密钥")
            elif response.status_code in (404, 405):
                # 一些MCP端点可能不支持GET根路径，返回405；视为端点可达，后续用POST尝试
                self.is_available = True
                logger.warning(f"MetaSota MCP服务器对GET返回 {response.status_code}，将尝试POST调用")
            else:
                logger.warning(f"MetaSota MCP服务器响应异常: {response.status_code}")
        except Exception as e:
            logger.warning(f"MetaSota MCP服务器连接失败: {e}")
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """使用MetaSota MCP服务器搜索"""
        if not self.is_available:
            logger.warning("MetaSota MCP服务器不可用，跳过搜索")
            logger.info("MetaSota搜索问题分析:")
            logger.info("1. MCP服务器端点返回HTML页面而非JSON")
            logger.info("2. 可能需要WebSocket连接或特殊MCP客户端")
            logger.info("3. 可能需要特殊的认证或配置")
            logger.info("建议: 联系ModelScope技术支持获取正确的MCP服务器使用方法")
            return []
        
        try:
            import requests
            import json
            from datetime import datetime, timedelta
            
            # MCP协议请求格式 - 使用正确的工具名称和参数
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "metaso_web_search",
                    "arguments": {
                        "q": query,
                        "size": self.max_articles,
                        "scope": "webpage",
                        "includeSummary": True,
                        "includeRawContent": False
                    }
                }
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'AI-News-Collector/1.0',
                'Accept': 'application/json'
            }
            
            logger.info(f"调用MetaSota MCP服务器: {query}")
            response = requests.post(
                self.mcp_base_url,
                json=mcp_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"MetaSota MCP响应: {data}")
                    
                    # 解析MetaSota MCP响应格式
                    if 'result' in data and 'content' in data['result']:
                        content = data['result']['content']
                        if content and isinstance(content, list) and len(content) > 0:
                            # MetaSota返回的是JSON字符串，需要解析
                            try:
                                json_str = content[0].get('text', '')
                                if json_str:
                                    parsed_data = json.loads(json_str)
                                    # 提取webpages数组
                                    results = parsed_data.get('webpages', [])
                                else:
                                    results = []
                            except (json.JSONDecodeError, KeyError) as e:
                                logger.warning(f"MetaSota响应解析失败: {e}")
                                results = []
                        else:
                            results = []
                    elif 'result' in data:
                        results = data['result'] if isinstance(data['result'], list) else []
                    else:
                        results = data.get('data', [])
                    
                    articles = []
                    for result in results:
                        if isinstance(result, dict):
                            # 计算发布时间
                            published_date = datetime.now()
                            if result.get('published_date') or result.get('date') or result.get('created_at'):
                                try:
                                    date_str = (result.get('published_date') or 
                                              result.get('date') or 
                                              result.get('created_at'))
                                    published_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                except:
                                    pass
                            
                            # 检查时间范围
                            if published_date >= datetime.now() - timedelta(days=days_back):
                                article = Article(
                                    title=result.get('title', result.get('headline', result.get('name', ''))),
                                    url=result.get('link', result.get('url', result.get('href', ''))),
                                    summary=result.get('snippet', result.get('summary', result.get('description', result.get('content', result.get('abstract', ''))))),
                                    published=published_date.isoformat(),
                                    author=result.get('authors', result.get('author', result.get('creator', 'MetaSota Search'))),
                                    source_name=result.get('source', result.get('domain', result.get('site', 'MetaSota'))),
                                    source='metasota_search'
                                )
                                articles.append(article)
                    
                    logger.info(f"MetaSota搜索返回 {len(articles)} 篇文章")
                    return articles[:self.max_articles]
                    
                except json.JSONDecodeError as e:
                    logger.error(f"MetaSota MCP响应JSON解析失败: {e}")
                    logger.debug(f"原始响应: {response.text[:500]}")
                    return []
            else:
                logger.error(f"MetaSota MCP服务器错误: {response.status_code} - {response.text[:200]}")
                return []
                
        except Exception as e:
            logger.error(f"MetaSota MCP搜索失败: {e}")
            return []