import types
from datetime import datetime, timedelta, timezone
import pytest

from ai_news_collector_lib.tools.search_tools import ArxivTool


class FakeResp:
    def __init__(self, content: bytes):
        self.content = content
        self.status_code = 200

    def raise_for_status(self):
        return None


def bs_raises(*args, **kwargs):
    # 强制 BeautifulSoup 解析失败，以触发 feedparser 回退逻辑
    raise Exception("Forced BeautifulSoup failure for fallback")


# 仅包含 updated 的 Atom 示例（用于 updated_parsed 回退）
ATOM_UPDATED = (
    """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Feed</title>
  <entry>
    <id>http://arxiv.org/abs/1234.5678</id>
    <title>Test Atom updated only</title>
    <summary>Summary</summary>
    <updated>2024-10-01T12:34:56Z</updated>
  </entry>
</feed>
"""
).encode("utf-8")


# 仅包含 published 的 Atom 示例（用于 published_parsed 回退）
ATOM_PUBLISHED = (
    """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Feed</title>
  <entry>
    <id>http://arxiv.org/abs/9876.5432</id>
    <title>Test Atom published only</title>
    <summary>Summary</summary>
    <published>2023-08-15T08:09:10Z</published>
  </entry>
</feed>
"""
).encode("utf-8")


# 不包含任何日期字段（用于 fallback 至 datetime.now）
ATOM_NO_DATES = (
    """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Feed</title>
  <entry>
    <id>http://arxiv.org/abs/0000.0000</id>
    <title>No dates entry</title>
    <summary>Summary</summary>
  </entry>
</feed>
"""
).encode("utf-8")


def _patch_requests_and_bs(monkeypatch, content_bytes: bytes):
    # patch BeautifulSoup to raise within module
    import ai_news_collector_lib.tools.search_tools as st
    monkeypatch.setattr(st, "BeautifulSoup", bs_raises)

    # patch requests.get in module scope to return our fake response
    def fake_get(url, timeout=30):
        return FakeResp(content_bytes)

    monkeypatch.setattr(st, "requests", types.SimpleNamespace(get=fake_get))


def test_arxiv_fallback_updated(monkeypatch):
    _patch_requests_and_bs(monkeypatch, ATOM_UPDATED)
    tool = ArxivTool(max_articles=1)
    # 避免被 _filter_by_date 误过滤，设置 days_back=0
    articles = tool.search("test", days_back=0)

    assert len(articles) == 1
    a = articles[0]
    # feedparser.updated_parsed -> datetime(*struct_time[:6])
    assert a.published.startswith("2024-10-01T12:34:56"), a.published
    assert a.source == "arxiv"
    assert a.source_name == "ArXiv"


def test_arxiv_fallback_published(monkeypatch):
    _patch_requests_and_bs(monkeypatch, ATOM_PUBLISHED)
    tool = ArxivTool(max_articles=1)
    # 避免被 _filter_by_date 误过滤，设置 days_back=0
    articles = tool.search("test", days_back=0)

    assert len(articles) == 1
    a = articles[0]
    assert a.published.startswith("2023-08-15T08:09:10"), a.published
    assert a.source == "arxiv"
    assert a.source_name == "ArXiv"


def test_arxiv_fallback_now(monkeypatch):
    _patch_requests_and_bs(monkeypatch, ATOM_NO_DATES)
    tool = ArxivTool(max_articles=1)
    start = datetime.now(timezone.utc) - timedelta(seconds=10)
    # 避免被 _filter_by_date 误过滤，设置 days_back=0
    articles = tool.search("test", days_back=0)
    end = datetime.now(timezone.utc) + timedelta(seconds=10)

    assert len(articles) == 1
    a = articles[0]
    # fallback 至 datetime.now()：断言在合理时间窗口内
    pub = datetime.fromisoformat(a.published.replace('Z', '+00:00'))
    assert start <= pub <= end, (start, pub, end)
    assert a.source == "arxiv"
    assert a.source_name == "ArXiv"