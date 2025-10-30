#!/usr/bin/env python3
"""
测试修复后的时间过滤功能
验证各个搜索引擎的时间过滤是否正常工作
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

class DateFilteringTester:
    """时间过滤功能测试器"""
    
    def __init__(self):
        self.config = SearchConfig()
        self.collector = AINewsCollector(self.config)
        
    def analyze_article_dates(self, articles: List[Article], days_back: int) -> Dict[str, Any]:
        """分析文章日期分布"""
        now = datetime.now(timezone.utc)
        cutoff_date = now - timedelta(days=days_back)
        
        analysis = {
            "total_articles": len(articles),
            "within_range": 0,
            "outside_range": 0,
            "invalid_dates": 0,
            "date_distribution": {},
            "oldest_article": None,
            "newest_article": None,
            "date_issues": []
        }
        
        valid_articles = []
        
        for article in articles:
            try:
                if not article.published:
                    analysis["invalid_dates"] += 1
                    continue
                
                # 处理不同的时间格式
                published_str = article.published
                if published_str.endswith("Z"):
                    published_str = published_str[:-1] + "+00:00"
                
                published_time = datetime.fromisoformat(published_str)
                valid_articles.append((article, published_time))
                
                # 统计日期分布
                days_old = (now - published_time).days
                if days_old <= 1:
                    analysis["date_distribution"]["0-1天"] = analysis["date_distribution"].get("0-1天", 0) + 1
                elif days_old <= 7:
                    analysis["date_distribution"]["1-7天"] = analysis["date_distribution"].get("1-7天", 0) + 1
                elif days_old <= 30:
                    analysis["date_distribution"]["7-30天"] = analysis["date_distribution"].get("7-30天", 0) + 1
                elif days_old <= 365:
                    analysis["date_distribution"]["30-365天"] = analysis["date_distribution"].get("30-365天", 0) + 1
                else:
                    analysis["date_distribution"]["1年以上"] = analysis["date_distribution"].get("1年以上", 0) + 1
                
                # 检查是否在时间范围内
                if published_time >= cutoff_date:
                    analysis["within_range"] += 1
                else:
                    analysis["outside_range"] += 1
                    analysis["date_issues"].append({
                        "title": article.title[:50] + "..." if len(article.title) > 50 else article.title,
                        "source": article.source,
                        "published": article.published,
                        "days_old": days_old
                    })
                
            except (ValueError, TypeError) as e:
                analysis["invalid_dates"] += 1
                analysis["date_issues"].append({
                    "title": article.title[:50] + "..." if len(article.title) > 50 else article.title,
                    "source": article.source,
                    "error": f"日期解析失败: {e}",
                    "published": article.published
                })
        
        # 找到最老和最新的文章
        if valid_articles:
            valid_articles.sort(key=lambda x: x[1])
            analysis["oldest_article"] = {
                "title": valid_articles[-1][0].title[:50] + "..." if len(valid_articles[-1][0].title) > 50 else valid_articles[-1][0].title,
                "source": valid_articles[-1][0].source,
                "published": valid_articles[-1][0].published,
                "days_old": (now - valid_articles[-1][1]).days
            }
            analysis["newest_article"] = {
                "title": valid_articles[0][0].title[:50] + "..." if len(valid_articles[0][0].title) > 50 else valid_articles[0][0].title,
                "source": valid_articles[0][0].source,
                "published": valid_articles[0][0].published,
                "days_old": (now - valid_articles[0][1]).days
            }
        
        return analysis
    
    async def test_single_source_detailed(self, source: str, query: str = "artificial intelligence", days_back: int = 1) -> Dict[str, Any]:
        """详细测试单个搜索源"""
        logger.info(f"详细测试搜索源: {source}")
        
        try:
            # 获取搜索结果
            tool = self.collector.tools.get(source)
            if not tool:
                return {"error": f"搜索源 {source} 不可用"}
            
            # 执行搜索
            articles = await asyncio.to_thread(tool.search, query, days_back)
            
            # 分析结果
            date_analysis = self.analyze_article_dates(articles, days_back)
            
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
    
    def generate_detailed_report(self, test_results: Dict[str, Any]) -> str:
        """生成详细的测试报告"""
        report = []
        report.append("=" * 80)
        report.append("AI新闻收集器时间过滤修复验证报告")
        report.append("=" * 80)
        report.append("")
        
        total_articles = 0
        total_within_range = 0
        total_outside_range = 0
        problematic_sources = []
        
        report.append("1. 各搜索源详细测试结果:")
        report.append("-" * 60)
        
        for source, result in test_results.items():
            if "error" in result:
                report.append(f"❌ {source}: 错误 - {result['error']}")
                continue
            
            articles_found = result.get("articles_found", 0)
            date_analysis = result.get("date_analysis", {})
            
            total_articles += articles_found
            total_within_range += date_analysis.get("within_range", 0)
            total_outside_range += date_analysis.get("outside_range", 0)
            
            report.append(f"✅ {source}: 找到 {articles_found} 篇文章")
            
            # 显示日期分布
            date_dist = date_analysis.get("date_distribution", {})
            if date_dist:
                report.append(f"   📊 日期分布:")
                for period, count in date_dist.items():
                    report.append(f"      {period}: {count} 篇")
            
            # 显示时间过滤效果
            within_range = date_analysis.get("within_range", 0)
            outside_range = date_analysis.get("outside_range", 0)
            
            if outside_range > 0:
                report.append(f"   ⚠️  时间过滤效果: {within_range} 篇在范围内, {outside_range} 篇超出范围")
                problematic_sources.append(source)
                
                # 显示最老的文章
                oldest = date_analysis.get("oldest_article")
                if oldest:
                    report.append(f"   📅 最老文章: {oldest['days_old']}天前 - {oldest['title']}")
            else:
                report.append(f"   ✅ 时间过滤效果: 所有 {within_range} 篇文章都在时间范围内")
            
            report.append("")
        
        report.append("2. 总体统计:")
        report.append("-" * 60)
        report.append(f"总文章数: {total_articles}")
        report.append(f"时间范围内: {total_within_range}")
        report.append(f"超出时间范围: {total_outside_range}")
        
        if total_articles > 0:
            accuracy = (total_within_range / total_articles) * 100
            report.append(f"时间过滤准确率: {accuracy:.1f}%")
        
        report.append("")
        
        report.append("3. 修复效果评估:")
        report.append("-" * 60)
        
        if problematic_sources:
            report.append(f"❌ 仍有问题的搜索源: {', '.join(problematic_sources)}")
            report.append("   这些搜索源仍然返回超出时间范围的文章")
        else:
            report.append("✅ 所有搜索源的时间过滤都正常工作")
        
        if total_outside_range == 0:
            report.append("🎉 时间过滤修复成功！所有文章都在指定时间范围内")
        else:
            report.append(f"⚠️  仍有 {total_outside_range} 篇文章超出时间范围，需要进一步优化")
        
        report.append("")
        
        report.append("4. 修复内容总结:")
        report.append("-" * 60)
        report.append("✅ Brave Search API: 添加了 freshness 参数支持")
        report.append("✅ Tavily API: 添加了 time_range 和 days 参数支持")
        report.append("✅ Serper API: 添加了客户端时间过滤")
        report.append("✅ MetaSota API: 优化了客户端时间过滤")
        report.append("✅ 所有API: 都添加了客户端时间过滤作为备用")
        
        return "\n".join(report)

async def main():
    """主函数"""
    tester = DateFilteringTester()
    
    # 测试所有搜索源
    test_results = {}
    available_sources = tester.collector.get_available_sources()
    
    for source in available_sources:
        result = await tester.test_single_source_detailed(source, "artificial intelligence", days_back=1)
        test_results[source] = result
    
    # 生成详细报告
    report = tester.generate_detailed_report(test_results)
    
    print(report)
    
    # 保存报告到文件
    with open("date_filtering_fix_verification_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n详细验证报告已保存到: date_filtering_fix_verification_report.txt")

if __name__ == "__main__":
    asyncio.run(main())
