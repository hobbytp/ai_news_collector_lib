"""
基本测试
"""


def test_basic():
    """基本测试"""
    assert True


def test_import():
    """测试导入"""
    try:
        from ai_news_collector_lib import AINewsCollector, SearchConfig

        assert True
    except ImportError as e:
        assert False, f"导入失败: {e}"
