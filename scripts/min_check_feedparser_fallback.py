#!/usr/bin/env python3
"""
最小化检查：验证 feedparser 条目在仅有 updated_parsed 或仅有 published_parsed 时，
日期提取逻辑能够正常工作且不抛异常。
无需网络请求。
"""

import sys
from datetime import datetime
import feedparser


def pick_date(entry):
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6])
        return None
    except Exception:
        return None


def test_published_parsed():
    rss = (
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
          <channel>
            <title>Test RSS</title>
            <link>http://example.com/</link>
            <description>desc</description>
            <item>
              <title>Item A</title>
              <link>http://example.com/a</link>
              <pubDate>Mon, 14 Oct 2024 12:34:56 GMT</pubDate>
            </item>
          </channel>
        </rss>
        """
    ).strip()
    feed = feedparser.parse(rss)
    assert feed.entries, "No entries parsed for RSS sample"
    dt = pick_date(feed.entries[0])
    assert dt is not None, "Failed to pick date from published_parsed"
    print("published_parsed ->", dt.isoformat())


def test_updated_parsed():
    atom = (
        """
        <?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <title>Test Atom</title>
          <updated>2024-10-14T12:35:00Z</updated>
          <id>urn:uuid:12345678-1234-1234-1234-1234567890ab</id>
          <entry>
            <title>Entry B</title>
            <id>urn:uuid:abcdefab-1234-5678-90ab-abcdefabcdef</id>
            <updated>2024-10-14T12:35:00Z</updated>
            <link href="http://example.org/"/>
          </entry>
        </feed>
        """
    ).strip()
    feed = feedparser.parse(atom)
    assert feed.entries, "No entries parsed for Atom sample"
    dt = pick_date(feed.entries[0])
    assert dt is not None, "Failed to pick date from updated_parsed"
    print("updated_parsed ->", dt.isoformat())


if __name__ == "__main__":
    try:
        test_published_parsed()
        test_updated_parsed()
        print("PASS: feedparser fallback path works without errors")
        sys.exit(0)
    except Exception as e:
        print("FAIL:", e)
        sys.exit(1)