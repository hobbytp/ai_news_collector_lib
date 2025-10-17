import pytest
from datetime import datetime


@pytest.mark.asyncio
@pytest.mark.network
async def test_collect_news_basic_network(collector, allow_network, vcr_vcr):
    if not allow_network:
        pytest.skip("Network disabled by .env (ALLOW_NETWORK != 1)")

    # 仅选择较稳定的免费源，降低波动
    sources = [s for s in collector.get_available_sources() if s in ("hackernews", "duckduckgo")]
    # 使用 VCR 录制/回放网络请求
    with vcr_vcr.use_cassette("basic_ai_hn_ddg.yaml"):
        result = await collector.collect_news(query="artificial intelligence", sources=sources)

    # 结构断言
    assert isinstance(result.total_articles, int)
    assert isinstance(result.unique_articles, int)
    assert isinstance(result.duplicates_removed, int)
    assert isinstance(result.source_progress, dict)

    for s in sources:
        assert s in result.source_progress
        assert result.source_progress[s]["status"] in {"completed", "failed", "pending"}

    # 文章字段基本有效性校验（如有）
    for a in result.articles:
        assert a.title
        assert a.url
        assert a.source in sources
        # published ISO 格式校验
        try:
            datetime.fromisoformat(a.published.replace("Z", "+00:00"))
        except Exception:
            pytest.fail(f"Article published not ISO format: {a.published}")