"""
高级使用示例
"""

import asyncio
from ai_news_collector_lib import AdvancedAINewsCollector, AdvancedSearchConfig


async def main():
    """高级使用示例"""
    # 创建高级配置
    config = AdvancedSearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        enable_content_extraction=True,
        enable_keyword_extraction=True,
        cache_results=True,
        max_articles_per_source=5,
    )

    # 创建高级收集器
    collector = AdvancedAINewsCollector(config)

    # 收集新闻
    result = await collector.collect_news_advanced("machine learning")

    print(f"收集到 {result['total_articles']} 篇文章")
    print(f"去重后: {result['unique_articles']} 篇")
    print(f"总字数: {result.get('total_words', 0):,}")
    print(f"平均阅读时间: {result.get('average_reading_time', 0)} 分钟")

    # 显示文章列表
    for i, article in enumerate(result["articles"][:3], 1):
        print(f"{i}. {article['title']}")
        print(f"   来源: {article['source_name']}")
        print(f"   字数: {article.get('word_count', 0)}")
        print(f"   阅读时间: {article.get('reading_time', 0)} 分钟")
        if article.get("keywords"):
            print(f"   关键词: {', '.join(article['keywords'][:3])}")
        print(f"   链接: {article['url']}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
