"""
基本使用示例
"""
import asyncio
from ai_news_collector_lib import AINewsCollector, SearchConfig

async def main():
    """基本使用示例"""
    # 创建配置
    config = SearchConfig(
        enable_hackernews=True,
        enable_arxiv=True,
        max_articles_per_source=5
    )
    
    # 创建收集器
    collector = AINewsCollector(config)
    
    # 收集新闻
    result = await collector.collect_news("artificial intelligence")
    
    print(f"收集到 {result.total_articles} 篇文章")
    print(f"去重后: {result.unique_articles} 篇")
    print(f"去重数量: {result.duplicates_removed}")
    
    # 显示文章列表
    for i, article in enumerate(result.articles[:3], 1):
        print(f"{i}. {article.title}")
        print(f"   来源: {article.source_name}")
        print(f"   链接: {article.url}")
        print()

if __name__ == "__main__":
    asyncio.run(main())


