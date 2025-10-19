import pytest


@pytest.mark.asyncio
@pytest.mark.network
async def test_collect_news_advanced_network(advanced_collector, allow_network, vcr_vcr):
    if not allow_network:
        pytest.skip("Network disabled by .env (ALLOW_NETWORK != 1)")

    # 仅选择较稳定的免费源，避免附加内容提取网络调用
    sources = [s for s in advanced_collector.get_available_sources() if s in ("hackernews", "duckduckgo")]
    # 使用 VCR 录制/回放网络请求
    with vcr_vcr.use_cassette("advanced_ml_hn_ddg.yaml"):
        result = await advanced_collector.collect_news_advanced(query="machine learning", sources=sources)

    assert isinstance(result, dict)
    assert "articles" in result
    assert isinstance(result["articles"], list)

    if result["articles"]:
        a = result["articles"][0]
        assert "keywords" in a
        assert isinstance(a["keywords"], list)
        assert "content" in a  # 可能为空字符串，因为禁用了内容提取