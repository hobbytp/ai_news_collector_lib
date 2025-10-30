#!/usr/bin/env python3
"""
时间过滤问题诊断工具
用于定位ai_news_collector_lib中时间过滤不准确的问题
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_news_collector_lib'))

from ai_news_collector_lib.config.settings import SearchConfig
from ai_news_collector_lib.core.collector import AINewsCollector
from ai_news_collector_lib.models.article import Article

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DateFilteringDiagnostic:
    """时间过滤诊断工具"""
    
    def __init__(self):
        self.config = SearchConfig()
        self.collector = AINewsCollector(self.config)
        
    def analyze_search_tools(self) -> Dict[str, Dict[str, Any]]:
        """分析各个搜索工具的时间过滤实现"""
        analysis = {}
        
        # 检查各个搜索工具的时间过滤实现
        tools_info = {
            "hackernews": {
                "has_date_filter": False,
                "description": "HackerNews工具没有实现时间过滤",
                "issue": "HackerNews API本身不提供时间过滤，只能获取最新文章"
            },
            "arxiv": {
                "has_date_filter": True,
                "description": "Arxiv工具使用sortBy=submittedDate和sortOrder=descending",
                "issue": "可能获取到较老的文章，因为Arxiv按提交时间排序，不是发布时间"
            },
            "duckduckgo": {
                "has_date_filter": True,
                "description": "DuckDuckGo工具使用after:日期格式过滤",
                "issue": "DuckDuckGo的时间过滤可能不够精确"
            },
            "newsapi": {
                "has_date_filter": True,
                "description": "NewsAPI工具使用from参数指定开始日期",
                "issue": "NewsAPI的时间过滤相对准确"
            },
            "tavily": {
                "has_date_filter": False,
                "description": "Tavily工具没有实现时间过滤",
                "issue": "Tavily API调用中没有使用时间参数"
            },
            "google_search": {
                "has_date_filter": True,
                "description": "Google搜索工具使用dateRestrict参数",
                "issue": "Google的dateRestrict参数可能不够精确"
            },
            "serper": {
                "has_date_filter": False,
                "description": "Serper工具没有实现时间过滤",
                "issue": "Serper API调用中没有使用时间参数"
            },
            "brave_search": {
                "has_date_filter": False,
                "description": "Brave搜索工具没有实现时间过滤",
                "issue": "Brave API调用中没有使用时间参数"
            },
            "metasota_search": {
                "has_date_filter": False,
                "description": "MetaSota搜索工具没有实现时间过滤",
                "issue": "MetaSota MCP调用中没有使用时间参数"
            }
        }
        
        return tools_info
    
    def check_article_dates(self, articles: List[Article], days_back: int) -> Dict[str, Any]:
        """检查文章日期是否符合要求"""
        now = datetime.now(timezone.utc)
        cutoff_date = now - timedelta(days=days_back)
        
        results = {
            "total_articles": len(articles),
            "within_date_range": 0,
            "outside_date_range": 0,
            "invalid_dates": 0,
            "old_articles": [],
            "date_analysis": []
        }
        
        for article in articles:
            try:
                if not article.published:
                    results["invalid_dates"] += 1
                    continue
                
                # 处理不同的时间格式
                published_str = article.published
                if published_str.endswith("Z"):
                    published_str = published_str[:-1] + "+00:00"
                
                published_time = datetime.fromisoformat(published_str)
                
                if published_time >= cutoff_date:
                    results["within_date_range"] += 1
                else:
                    results["outside_date_range"] += 1
                    days_old = (now - published_time).days
                    results["old_articles"].append({
                        "title": article.title[:50] + "..." if len(article.title) > 50 else article.title,
                        "source": article.source,
                        "published": article.published,
                        "days_old": days_old
                    })
                
                results["date_analysis"].append({
                    "source": article.source,
                    "published": article.published,
                    "is_recent": published_time >= cutoff_date,
                    "days_old": (now - published_time).days if published_time < now else 0
                })
                
            except (ValueError, TypeError) as e:
                results["invalid_dates"] += 1
                logger.warning(f"无法解析日期: {article.published} - {e}")
        
        return results
    
    async def test_single_source(self, source: str, query: str = "artificial intelligence", days_back: int = 1) -> Dict[str, Any]:
        """测试单个搜索源"""
        logger.info(f"测试搜索源: {source}")
        
        try:
            # 获取单个源的搜索结果
            tool = self.collector.tools.get(source)
            if not tool:
                return {"error": f"搜索源 {source} 不可用"}
            
            # 执行搜索
            articles = await asyncio.to_thread(tool.search, query, days_back)
            
            # 分析结果
            date_analysis = self.check_article_dates(articles, days_back)
            
            return {
                "source": source,
                "articles_found": len(articles),
                "date_analysis": date_analysis,
                "tool_info": {
                    "name": tool.__class__.__name__,
                    "description": getattr(tool, "description", ""),
                    "max_articles": getattr(tool, "max_articles", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"测试搜索源 {source} 失败: {e}")
            return {"error": str(e)}
    
    async def test_all_sources(self, query: str = "artificial intelligence", days_back: int = 1) -> Dict[str, Any]:
        """测试所有可用的搜索源"""
        logger.info(f"开始测试所有搜索源，查询: {query}, 天数: {days_back}")
        
        available_sources = self.collector.get_available_sources()
        logger.info(f"可用的搜索源: {available_sources}")
        
        results = {}
        
        # 并发测试所有源
        tasks = []
        for source in available_sources:
            task = self.test_single_source(source, query, days_back)
            tasks.append(task)
        
        if tasks:
            test_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(test_results):
                source = available_sources[i]
                if isinstance(result, Exception):
                    results[source] = {"error": str(result)}
                else:
                    results[source] = result
        
        return results
    
    def generate_report(self, test_results: Dict[str, Any]) -> str:
        """生成诊断报告"""
        report = []
        report.append("=" * 80)
        report.append("AI新闻收集器时间过滤问题诊断报告")
        report.append("=" * 80)
        report.append("")
        
        # 分析各个搜索工具的实现
        tools_analysis = self.analyze_search_tools()
        
        report.append("1. 搜索工具时间过滤实现分析:")
        report.append("-" * 50)
        
        problematic_sources = []
        for source, info in tools_analysis.items():
            status = "✓" if info["has_date_filter"] else "✗"
            report.append(f"{status} {source}: {info['description']}")
            if not info["has_date_filter"]:
                problematic_sources.append(source)
                report.append(f"   问题: {info['issue']}")
        
        report.append("")
        report.append("2. 实际测试结果:")
        report.append("-" * 50)
        
        total_articles = 0
        total_old_articles = 0
        
        for source, result in test_results.items():
            if "error" in result:
                report.append(f"✗ {source}: 错误 - {result['error']}")
                continue
            
            articles_found = result.get("articles_found", 0)
            date_analysis = result.get("date_analysis", {})
            
            total_articles += articles_found
            total_old_articles += date_analysis.get("outside_date_range", 0)
            
            report.append(f"✓ {source}: 找到 {articles_found} 篇文章")
            
            if date_analysis.get("outside_date_range", 0) > 0:
                report.append(f"  ⚠️  其中 {date_analysis['outside_date_range']} 篇超出时间范围")
                
                # 显示最老的文章
                old_articles = date_analysis.get("old_articles", [])
                if old_articles:
                    oldest = max(old_articles, key=lambda x: x["days_old"])
                    report.append(f"  📅 最老文章: {oldest['days_old']}天前 - {oldest['title']}")
        
        report.append("")
        report.append("3. 问题总结:")
        report.append("-" * 50)
        
        if problematic_sources:
            report.append(f"❌ 以下搜索源没有实现时间过滤: {', '.join(problematic_sources)}")
        
        if total_old_articles > 0:
            report.append(f"❌ 总共发现 {total_old_articles} 篇超出时间范围的文章")
            report.append("   建议检查这些搜索源的时间过滤实现")
        
        report.append("")
        report.append("4. 修复建议:")
        report.append("-" * 50)
        
        for source in problematic_sources:
            if source == "hackernews":
                report.append(f"• {source}: 考虑在客户端进行时间过滤")
            elif source in ["tavily", "serper", "brave_search", "metasota_search"]:
                report.append(f"• {source}: 检查API文档，添加时间过滤参数")
            else:
                report.append(f"• {source}: 检查时间过滤参数是否正确传递")
        
        report.append("")
        report.append("5. 代码位置:")
        report.append("-" * 50)
        report.append("• 搜索工具实现: ai_news_collector_lib/tools/search_tools.py")
        report.append("• 时间过滤逻辑: BaseSearchTool._filter_by_date()")
        report.append("• 配置设置: ai_news_collector_lib/config/settings.py")
        
        return "\n".join(report)

async def main():
    """主函数"""
    diagnostic = DateFilteringDiagnostic()
    
    # 测试所有搜索源
    test_results = await diagnostic.test_all_sources("artificial intelligence", days_back=1)
    
    # 生成报告
    report = diagnostic.generate_report(test_results)
    
    print(report)
    
    # 保存报告到文件
    with open("date_filtering_diagnostic_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n诊断报告已保存到: date_filtering_diagnostic_report.txt")

if __name__ == "__main__":
    asyncio.run(main())
