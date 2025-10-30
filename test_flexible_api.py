#!/usr/bin/env python3
"""
测试灵活API接口
注：该文件用于交互式演示，默认不参与CI测试（无VCR录制）。
"""

# 在pytest收集时跳过该模块，避免离线回放失败
try:  # 仅在pytest存在时执行
    import pytest  # type: ignore

    pytest.skip(
        "test_flexible_api.py 仅用于手动演示，CI离线测试中跳过",
        allow_module_level=True,
    )
except Exception:
    pass

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_news_collector_lib import (
    FlexibleSearchConfig, 
    TimeRange, 
    FlexibleAINewsCollector,
    collect_with_single_engine,
    collect_with_multiple_engines
)


async def test_single_engine():
    """测试单个搜索引擎"""
    print("=== 测试单个搜索引擎 ===")
    
    try:
        result = await collect_with_single_engine(
            engine_name="hackernews",
            query="artificial intelligence",
            time_range=TimeRange.ONE_WEEK,
            max_articles=5
        )
        
        print(f"✅ HackerNews搜索成功: {result.unique_articles} 篇文章")
        for i, article in enumerate(result.articles[:3], 1):
            print(f"  {i}. {article.title}")
        
        return True
    except Exception as e:
        print(f"❌ HackerNews搜索失败: {e}")
        return False


async def test_multiple_engines():
    """测试多个搜索引擎"""
    print("\n=== 测试多个搜索引擎 ===")
    
    try:
        result = await collect_with_multiple_engines(
            engine_names=["hackernews", "arxiv"],
            query="machine learning",
            time_range=TimeRange.ONE_WEEK,
            max_articles_per_engine=3
        )
        
        print(f"✅ 多引擎搜索成功: {result.unique_articles} 篇文章")
        print(f"  总文章数: {result.total_articles}")
        print(f"  去重后: {result.unique_articles}")
        print(f"  去重数: {result.duplicates_removed}")
        
        return True
    except Exception as e:
        print(f"❌ 多引擎搜索失败: {e}")
        return False


async def test_flexible_config():
    """测试灵活配置"""
    print("\n=== 测试灵活配置 ===")
    
    try:
        # 创建配置
        config = FlexibleSearchConfig()
        
        # 配置HackerNews
        config.set_engine_config(
            engine_name="hackernews",
            enabled=True,
            max_articles=3,
            time_range=TimeRange.ONE_DAY
        )
        
        # 配置ArXiv
        config.set_engine_config(
            engine_name="arxiv",
            enabled=True,
            max_articles=3,
            time_range=TimeRange.ONE_WEEK
        )
        
        # 创建收集器
        collector = FlexibleAINewsCollector(config)
        
        # 搜索
        result = await collector.collect_news("deep learning")
        
        print(f"✅ 灵活配置搜索成功: {result.unique_articles} 篇文章")
        
        # 显示引擎信息
        engine_info = collector.get_engine_info()
        for engine_name, info in engine_info.items():
            print(f"  {engine_name}: {info['time_range']}, {info['max_articles']} 篇")
        
        return True
    except Exception as e:
        print(f"❌ 灵活配置搜索失败: {e}")
        return False


async def test_time_range_presets():
    """测试时间范围预设"""
    print("\n=== 测试时间范围预设 ===")
    
    try:
        config = FlexibleSearchConfig()
        config.set_engine_config("hackernews", enabled=True, max_articles=2)
        
        collector = FlexibleAINewsCollector(config)
        
        # 测试不同时间范围
        time_ranges = [
            (TimeRange.ONE_DAY, "一天"),
            (TimeRange.ONE_WEEK, "一周"),
            (TimeRange.ONE_MONTH, "一个月"),
            (TimeRange.ONE_YEAR, "一年")
        ]
        
        for time_range, desc in time_ranges:
            collector.set_time_range_for_engine("hackernews", time_range)
            result = await collector.collect_news("AI")
            print(f"  {desc}: {result.unique_articles} 篇文章")
        
        print("✅ 时间范围预设测试成功")
        return True
    except Exception as e:
        print(f"❌ 时间范围预设测试失败: {e}")
        return False


async def test_dynamic_config_update():
    """测试动态配置更新"""
    print("\n=== 测试动态配置更新 ===")
    
    try:
        config = FlexibleSearchConfig()
        config.set_engine_config("hackernews", enabled=True, max_articles=2)
        
        collector = FlexibleAINewsCollector(config)
        
        # 初始搜索
        result1 = await collector.collect_news("AI")
        print(f"初始搜索: {result1.unique_articles} 篇文章")
        
        # 更新配置
        collector.update_engine_config(
            engine_name="hackernews",
            max_articles=5,
            time_range=TimeRange.ONE_WEEK
        )
        
        # 再次搜索
        result2 = await collector.collect_news("AI")
        print(f"更新后搜索: {result2.unique_articles} 篇文章")
        
        print("✅ 动态配置更新测试成功")
        return True
    except Exception as e:
        print(f"❌ 动态配置更新测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始测试灵活API接口\n")
    
    tests = [
        test_single_engine,
        test_multiple_engines,
        test_flexible_config,
        test_time_range_presets,
        test_dynamic_config_update
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️  部分测试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
