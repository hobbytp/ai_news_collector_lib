#!/usr/bin/env python3
"""
AI News Collector Library CLI
命令行接口工具
"""

import asyncio
import argparse
import logging
import sys
from typing import List, Optional
from datetime import datetime

from ai_news_collector_lib import AINewsCollector, AdvancedAINewsCollector
from ai_news_collector_lib.config import SearchConfig, AdvancedSearchConfig
from ai_news_collector_lib.utils import ReportGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_basic_config(args) -> SearchConfig:
    """创建基础配置"""
    config = SearchConfig(
        enable_hackernews=args.hackernews,
        enable_arxiv=args.arxiv,
        enable_duckduckgo=args.duckduckgo,
        enable_newsapi=args.newsapi,
        max_articles_per_source=args.max_articles,
        days_back=args.days_back,
        similarity_threshold=args.similarity_threshold,
    )

    # 设置API密钥
    if args.newsapi_key:
        config.newsapi_key = args.newsapi_key

    return config


def create_advanced_config(args) -> AdvancedSearchConfig:
    """创建高级配置"""
    config = AdvancedSearchConfig(
        enable_hackernews=args.hackernews,
        enable_arxiv=args.arxiv,
        enable_duckduckgo=args.duckduckgo,
        enable_newsapi=args.newsapi,
        enable_content_extraction=args.content_extraction,
        enable_keyword_extraction=args.keyword_extraction,
        cache_results=args.cache,
        max_articles_per_source=args.max_articles,
        days_back=args.days_back,
        similarity_threshold=args.similarity_threshold,
    )

    # 设置API密钥
    if args.newsapi_key:
        config.newsapi_key = args.newsapi_key

    return config


async def collect_news_basic(args):
    """基础新闻收集"""
    config = create_basic_config(args)
    collector = AINewsCollector(config)

    print(f"开始收集新闻: {args.query}")
    print(f"搜索源: {', '.join(collector.get_available_sources())}")

    result = await collector.collect_news(args.query)

    print(f"\n收集结果:")
    print(f"  总文章数: {result.total_articles}")
    print(f"  独特文章数: {result.unique_articles}")
    print(f"  去重数量: {result.duplicates_removed}")

    # 显示各源统计
    print(f"\n各源统计:")
    for source, progress in result.source_progress.items():
        status = "✅" if progress["status"] == "completed" else "❌"
        print(f"  {status} {source}: {progress['articles_found']} 篇文章")

    # 显示文章列表
    if args.show_articles:
        print(f"\n文章列表:")
        for i, article in enumerate(result.articles[: args.limit], 1):
            print(f"{i}. {article.title}")
            print(f"   来源: {article.source_name}")
            print(f"   链接: {article.url}")
            print(f"   摘要: {article.summary[:100]}...")
            print()

    return result


async def collect_news_advanced(args):
    """高级新闻收集"""
    config = create_advanced_config(args)
    collector = AdvancedAINewsCollector(config)

    print(f"开始高级新闻收集: {args.query}")
    print(f"搜索源: {', '.join(collector.get_available_sources())}")

    result = await collector.collect_news_advanced(args.query)

    print(f"\n收集结果:")
    print(f"  总文章数: {result['total_articles']}")
    print(f"  独特文章数: {result['unique_articles']}")
    print(f"  去重数量: {result['duplicates_removed']}")
    print(f"  总字数: {result.get('total_words', 0):,}")
    print(f"  平均阅读时间: {result.get('average_reading_time', 0)} 分钟")

    # 显示各源统计
    print(f"\n各源统计:")
    for source, progress in result["source_progress"].items():
        status = "✅" if progress["status"] == "completed" else "❌"
        print(f"  {status} {source}: {progress['articles_found']} 篇文章")

    # 显示文章列表
    if args.show_articles:
        print(f"\n文章列表:")
        for i, article in enumerate(result["articles"][: args.limit], 1):
            print(f"{i}. {article['title']}")
            print(f"   来源: {article['source_name']}")
            print(f"   字数: {article.get('word_count', 0)}")
            print(f"   阅读时间: {article.get('reading_time', 0)} 分钟")
            if article.get("keywords"):
                print(f"   关键词: {', '.join(article['keywords'][:3])}")
            print(f"   链接: {article['url']}")
            print()

    return result


def generate_report(args, result):
    """生成报告"""
    if not args.report:
        return

    reporter = ReportGenerator(output_dir=args.output_dir)

    print(f"\n生成报告...")

    # 生成Markdown报告
    if args.report_format in ["markdown", "all"]:
        markdown_file = reporter.save_report(result, format="markdown")
        print(f"Markdown报告: {markdown_file}")

    # 生成HTML报告
    if args.report_format in ["html", "all"]:
        html_file = reporter.save_report(result, format="html")
        print(f"HTML报告: {html_file}")

    # 生成JSON报告
    if args.report_format in ["json", "all"]:
        json_file = reporter.save_report(result, format="json")
        print(f"JSON报告: {json_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI News Collector Library - 收集AI相关新闻的命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基础收集
  ai-news-collector collect "artificial intelligence" --hackernews --arxiv
  
  # 高级收集
  ai-news-collector collect-advanced "machine learning" --content-extraction --keyword-extraction
  
  # 生成报告
  ai-news-collector collect "AI news" --report --report-format markdown
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 基础收集命令
    collect_parser = subparsers.add_parser("collect", help="基础新闻收集")
    collect_parser.add_argument("query", help="搜索查询")
    collect_parser.add_argument("--hackernews", action="store_true", help="启用HackerNews")
    collect_parser.add_argument("--arxiv", action="store_true", help="启用ArXiv")
    collect_parser.add_argument("--duckduckgo", action="store_true", help="启用DuckDuckGo")
    collect_parser.add_argument("--newsapi", action="store_true", help="启用NewsAPI")
    collect_parser.add_argument("--newsapi-key", help="NewsAPI密钥")
    collect_parser.add_argument("--max-articles", type=int, default=10, help="每个源最大文章数")
    collect_parser.add_argument("--days-back", type=int, default=7, help="搜索天数")
    collect_parser.add_argument(
        "--similarity-threshold", type=float, default=0.85, help="去重相似度阈值"
    )
    collect_parser.add_argument("--show-articles", action="store_true", help="显示文章列表")
    collect_parser.add_argument("--limit", type=int, default=10, help="显示文章数量限制")
    collect_parser.add_argument("--report", action="store_true", help="生成报告")
    collect_parser.add_argument(
        "--report-format",
        choices=["markdown", "html", "json", "all"],
        default="markdown",
        help="报告格式",
    )
    collect_parser.add_argument("--output-dir", default="./reports", help="输出目录")

    # 高级收集命令
    advanced_parser = subparsers.add_parser("collect-advanced", help="高级新闻收集")
    advanced_parser.add_argument("query", help="搜索查询")
    advanced_parser.add_argument("--hackernews", action="store_true", help="启用HackerNews")
    advanced_parser.add_argument("--arxiv", action="store_true", help="启用ArXiv")
    advanced_parser.add_argument("--duckduckgo", action="store_true", help="启用DuckDuckGo")
    advanced_parser.add_argument("--newsapi", action="store_true", help="启用NewsAPI")
    advanced_parser.add_argument("--newsapi-key", help="NewsAPI密钥")
    advanced_parser.add_argument("--content-extraction", action="store_true", help="启用内容提取")
    advanced_parser.add_argument("--keyword-extraction", action="store_true", help="启用关键词提取")
    advanced_parser.add_argument("--cache", action="store_true", help="启用缓存")
    advanced_parser.add_argument("--max-articles", type=int, default=10, help="每个源最大文章数")
    advanced_parser.add_argument("--days-back", type=int, default=7, help="搜索天数")
    advanced_parser.add_argument(
        "--similarity-threshold", type=float, default=0.85, help="去重相似度阈值"
    )
    advanced_parser.add_argument("--show-articles", action="store_true", help="显示文章列表")
    advanced_parser.add_argument("--limit", type=int, default=10, help="显示文章数量限制")
    advanced_parser.add_argument("--report", action="store_true", help="生成报告")
    advanced_parser.add_argument(
        "--report-format",
        choices=["markdown", "html", "json", "all"],
        default="markdown",
        help="报告格式",
    )
    advanced_parser.add_argument("--output-dir", default="./reports", help="输出目录")

    # 版本命令
    version_parser = subparsers.add_parser("version", help="显示版本信息")

    args = parser.parse_args()

    if args.command == "version":
        from ai_news_collector_lib import __version__

        print(f"AI News Collector Library v{__version__}")
        return

    if args.command == "collect":
        result = asyncio.run(collect_news_basic(args))
        generate_report(args, result)

    elif args.command == "collect-advanced":
        result = asyncio.run(collect_news_advanced(args))
        generate_report(args, result)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
