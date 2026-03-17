"""
Tests for the 4 new search engine tools:
YouTubeTool, GitHubSearchTool, HuggingFaceTool, PerplexityTool

Uses mock HTTP responses — no real API calls.
"""

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

from ai_news_collector_lib.tools.search_tools import (
    BaseSearchTool,
    YouTubeTool,
    GitHubSearchTool,
    HuggingFaceTool,
    PerplexityTool,
    BaiduSearchTool,
)


# ─────────────────────── Fixtures ─────────────────────────

RECENT_UTC_Z = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)
RECENT_UTC_OFFSET = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

MOCK_YOUTUBE_RESPONSE = {
    "items": [
        {
            "id": {"videoId": "abc123"},
            "snippet": {
                "title": "AI &amp; Machine Learning in 2026",
                "description": "A comprehensive overview of the latest AI trends.",
                "publishedAt": RECENT_UTC_Z,
                "channelTitle": "TechChannel",
            },
        },
        {
            "id": {"videoId": "def456"},
            "snippet": {
                "title": "Deep Learning Tutorial",
                "description": "Learn deep learning from scratch.",
                "publishedAt": RECENT_UTC_Z,
                "channelTitle": "LearnAI",
            },
        },
    ]
}

MOCK_GITHUB_RESPONSE = {
    "items": [
        {
            "full_name": "openai/gpt-5",
            "name": "gpt-5",
            "html_url": "https://github.com/openai/gpt-5",
            "description": "Next generation language model",
            "stargazers_count": 50000,
            "language": "Python",
            "pushed_at": RECENT_UTC_Z,
            "updated_at": RECENT_UTC_Z,
            "owner": {"login": "openai"},
        },
    ]
}

MOCK_HUGGINGFACE_RESPONSE = [
    {
        "modelId": "meta-llama/Llama-4",
        "id": "meta-llama/Llama-4",
        "lastModified": RECENT_UTC_Z,
        "pipeline_tag": "text-generation",
        "downloads": 1000000,
        "likes": 5000,
        "tags": ["pytorch", "llama", "text-generation", "en", "arxiv:2401.00001"],
    },
]

MOCK_PERPLEXITY_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": (
                    "Recent developments in AI show significant progress. "
                    "OpenAI released GPT-5 [1] with improved reasoning. "
                    "Meanwhile, Google DeepMind published Gemini 3.0 [2] "
                    "with multimodal capabilities."
                ),
            }
        }
    ],
    "citations": [
        "https://openai.com/blog/gpt-5",
        "https://deepmind.google/gemini-3",
    ],
}

MOCK_BAIDU_RESPONSE = {
    "data": {
        "web": [
            {
                "title": "Baidu AI Search Launches New Features",
                "url": "https://example.com/baidu-ai-search",
                "summary": "Baidu introduces enhanced AI search capabilities.",
                "site_name": "Example News",
                "page_time": RECENT_UTC_Z,
            },
            {
                "title": "Qianfan API Update",
                "url": "https://cloud.baidu.com/doc/qianfan-api",
                "content": "Qianfan web_search now supports richer filters.",
                "source": "Baidu Cloud",
                "publish_time": RECENT_UTC_OFFSET,
            },
        ]
    }
}


def _mock_response(json_data, status_code=200, headers=None):
    """Create a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.headers = headers or {}
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return resp


def _mock_session(response):
    """Create a mock session that returns the given response for get/post."""
    session = MagicMock()
    session.get.return_value = response
    session.post.return_value = response
    return session


# ─────────────────── BaseSearchTool Tests ─────────────────

class TestBaseSearchTool:
    """Test BaseSearchTool helper methods."""

    def test_parse_iso_datetime_with_z_suffix(self):
        result = BaseSearchTool._parse_iso_datetime("2026-02-18T10:00:00Z")
        assert "2026-02-18" in result
        assert "+00:00" in result

    def test_parse_iso_datetime_with_offset(self):
        result = BaseSearchTool._parse_iso_datetime("2026-02-18T18:00:00+08:00")
        assert "2026-02-18" in result

    def test_parse_iso_datetime_empty_string(self):
        result = BaseSearchTool._parse_iso_datetime("")
        # Should return current time, just check it's a valid ISO string
        dt = datetime.fromisoformat(result)
        assert dt is not None

    def test_parse_iso_datetime_invalid(self):
        result = BaseSearchTool._parse_iso_datetime("not-a-date")
        dt = datetime.fromisoformat(result)
        assert dt is not None

    def test_parse_iso_datetime_naive(self):
        result = BaseSearchTool._parse_iso_datetime("2026-02-18T10:00:00")
        assert "+00:00" in result  # Should add UTC timezone

    def test_build_session_returns_session(self):
        session = BaseSearchTool._build_session()
        assert hasattr(session, "get")
        assert hasattr(session, "post")


# ─────────────────── YouTubeTool Tests ─────────────────

class TestYouTubeTool:
    """Test YouTubeTool with mock API responses."""

    def test_initialization(self):
        tool = YouTubeTool(api_key="test-key")
        assert tool.api_key == "test-key"
        assert tool.max_articles == 10
        assert tool.relevance_language is None

    def test_initialization_with_language(self):
        tool = YouTubeTool(api_key="test-key", relevance_language="zh")
        assert tool.relevance_language == "zh"

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_success(self, mock_build_session):
        mock_build_session.return_value = _mock_session(
            _mock_response(MOCK_YOUTUBE_RESPONSE)
        )

        tool = YouTubeTool(api_key="test-key", max_articles=10)
        articles = tool.search("AI news", days_back=7)

        assert len(articles) == 2
        assert articles[0].source == "youtube"
        assert articles[0].url == "https://www.youtube.com/watch?v=abc123"
        # HTML entity should be unescaped
        assert "&amp;" not in articles[0].title
        assert "&" in articles[0].title
        assert articles[0].author == "TechChannel"

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_empty_response(self, mock_build_session):
        mock_build_session.return_value = _mock_session(
            _mock_response({"items": []})
        )

        tool = YouTubeTool(api_key="test-key")
        articles = tool.search("AI news")

        assert len(articles) == 0

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_api_error(self, mock_build_session):
        mock_build_session.return_value = _mock_session(
            _mock_response({}, status_code=403)
        )

        tool = YouTubeTool(api_key="test-key")
        articles = tool.search("AI news")

        assert len(articles) == 0


# ─────────────────── GitHubSearchTool Tests ─────────────────

class TestGitHubSearchTool:
    """Test GitHubSearchTool with mock API responses."""

    def test_initialization_without_key(self):
        tool = GitHubSearchTool()
        assert tool.api_key is None
        assert tool.max_articles == 10

    def test_initialization_with_key(self):
        tool = GitHubSearchTool(api_key="ghp_test123")
        assert tool.api_key == "ghp_test123"

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_success(self, mock_build_session):
        mock_build_session.return_value = _mock_session(
            _mock_response(MOCK_GITHUB_RESPONSE)
        )

        tool = GitHubSearchTool(api_key="ghp_test")
        articles = tool.search("LLM", days_back=7)

        assert len(articles) == 1
        assert articles[0].title == "openai/gpt-5"
        assert articles[0].source == "github"
        assert articles[0].author == "openai"
        assert "⭐ 50000" in articles[0].summary
        assert "Python" in articles[0].summary

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_without_auth(self, mock_build_session):
        """GitHub should work without API key."""
        session = _mock_session(_mock_response(MOCK_GITHUB_RESPONSE))
        mock_build_session.return_value = session

        tool = GitHubSearchTool()  # No API key
        articles = tool.search("AI", days_back=7)

        assert len(articles) == 1
        # Verify Authorization header was NOT set
        call_kwargs = session.get.call_args
        headers = call_kwargs.kwargs.get("headers", call_kwargs[1].get("headers", {}))
        assert "Authorization" not in headers

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_rate_limited(self, mock_build_session):
        """Test 403 rate limit handling."""
        resp = _mock_response({}, status_code=403)
        resp.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1740000000",
        }
        resp.raise_for_status = MagicMock()  # Don't raise, we check 403 manually
        mock_build_session.return_value = _mock_session(resp)

        tool = GitHubSearchTool()
        articles = tool.search("AI")

        assert len(articles) == 0  # Should return empty, not raise


# ─────────────────── HuggingFaceTool Tests ─────────────────

class TestHuggingFaceTool:
    """Test HuggingFaceTool with mock API responses."""

    def test_initialization_without_key(self):
        tool = HuggingFaceTool()
        assert tool.api_key is None

    def test_initialization_with_key(self):
        tool = HuggingFaceTool(api_key="hf_test123")
        assert tool.api_key == "hf_test123"

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_success(self, mock_build_session):
        mock_build_session.return_value = _mock_session(
            _mock_response(MOCK_HUGGINGFACE_RESPONSE)
        )

        tool = HuggingFaceTool(api_key="hf_test")
        articles = tool.search("llama", days_back=7)

        assert len(articles) == 1
        assert articles[0].title == "meta-llama/Llama-4"
        assert articles[0].source == "huggingface"
        assert articles[0].url == "https://huggingface.co/meta-llama/Llama-4"
        assert articles[0].author == "meta-llama"
        assert "text-generation" in articles[0].summary
        assert "1,000,000" in articles[0].summary  # formatted with commas

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_empty_list(self, mock_build_session):
        mock_build_session.return_value = _mock_session(
            _mock_response([])
        )

        tool = HuggingFaceTool()
        articles = tool.search("nonexistent")

        assert len(articles) == 0

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_non_list_response(self, mock_build_session):
        """HuggingFace API may return non-list (e.g. error object)."""
        mock_build_session.return_value = _mock_session(
            _mock_response({"error": "some error"})
        )

        tool = HuggingFaceTool()
        articles = tool.search("test")

        assert len(articles) == 0  # Should handle gracefully


# ─────────────────── PerplexityTool Tests ─────────────────

class TestPerplexityTool:
    """Test PerplexityTool with mock API responses."""

    def test_initialization(self):
        tool = PerplexityTool(api_key="pplx-test")
        assert tool.api_key == "pplx-test"
        assert tool.model == "sonar"

    def test_initialization_custom_model(self):
        tool = PerplexityTool(api_key="pplx-test", model="sonar-pro")
        assert tool.model == "sonar-pro"

    def test_map_citations_to_content(self):
        tool = PerplexityTool(api_key="test")

        content = (
            "OpenAI released GPT-5 [1] with improved reasoning. "
            "Google published Gemini 3.0 [2] with multimodal support."
        )
        result = tool._map_citations_to_content(content, num_citations=2)

        assert 0 in result
        assert 1 in result
        assert "GPT-5" in result[0]
        assert "Gemini" in result[1]

    def test_map_citations_no_markers(self):
        tool = PerplexityTool(api_key="test")
        result = tool._map_citations_to_content("No citations here.", num_citations=2)
        assert len(result) == 0

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_with_citations(self, mock_build_session):
        mock_build_session.return_value = _mock_session(
            _mock_response(MOCK_PERPLEXITY_RESPONSE)
        )

        tool = PerplexityTool(api_key="pplx-test")
        articles = tool.search("AI news", days_back=7)

        assert len(articles) == 2
        assert articles[0].source == "perplexity"
        assert articles[0].url == "https://openai.com/blog/gpt-5"
        assert articles[0].source_name == "openai.com"
        assert articles[1].url == "https://deepmind.google/gemini-3"

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_no_citations_fallback(self, mock_build_session):
        """When no citations, should return single article with LLM summary."""
        response_data = {
            "choices": [
                {"message": {"content": "Here is a summary of AI news."}}
            ],
            "citations": [],
        }
        mock_build_session.return_value = _mock_session(
            _mock_response(response_data)
        )

        tool = PerplexityTool(api_key="pplx-test")
        articles = tool.search("AI news")

        assert len(articles) == 1
        assert articles[0].title.startswith("Perplexity AI Summary")
        assert "perplexity.ai" in articles[0].url
        # URL should be properly encoded
        assert "%20" in articles[0].url or "+" in articles[0].url

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_empty_response(self, mock_build_session):
        """When API returns empty choices and no citations."""
        mock_build_session.return_value = _mock_session(
            _mock_response({"choices": [], "citations": []})
        )

        tool = PerplexityTool(api_key="pplx-test")
        articles = tool.search("AI")

        assert len(articles) == 0

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_api_error(self, mock_build_session):
        mock_build_session.return_value = _mock_session(
            _mock_response({}, status_code=500)
        )

        tool = PerplexityTool(api_key="pplx-test")
        articles = tool.search("AI")

        assert len(articles) == 0


class TestBaiduSearchTool:
    """Test BaiduSearchTool with mock API responses."""

    def test_initialization(self):
        tool = BaiduSearchTool(api_key="baidu-test-key")
        assert tool.api_key == "baidu-test-key"
        assert tool.max_articles == 10

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_success(self, mock_build_session):
        session = _mock_session(_mock_response(MOCK_BAIDU_RESPONSE))
        mock_build_session.return_value = session

        tool = BaiduSearchTool(api_key="baidu-test-key", max_articles=5)
        articles = tool.search("AI 搜索", days_back=7)

        assert len(articles) == 2
        assert articles[0].source == "baidu_search"
        assert articles[0].title == "Baidu AI Search Launches New Features"
        assert articles[0].url == "https://example.com/baidu-ai-search"
        assert articles[0].source_name == "Example News"

        call_kwargs = session.post.call_args.kwargs
        assert call_kwargs["headers"]["Authorization"] == "Bearer baidu-test-key"
        assert call_kwargs["json"]["messages"]["content"] == "AI 搜索"
        assert call_kwargs["json"]["search_source"] == "baidu_search_v2"
        assert "search_filter" in call_kwargs["json"]
        assert "page_time" in call_kwargs["json"]["search_filter"]["range"]

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_handles_empty_response(self, mock_build_session):
        mock_build_session.return_value = _mock_session(_mock_response({}))

        tool = BaiduSearchTool(api_key="baidu-test-key", max_articles=3)
        articles = tool.search("AI")

        assert articles == []

    @patch.object(BaseSearchTool, "_build_session")
    def test_search_api_error(self, mock_build_session):
        mock_build_session.return_value = _mock_session(
            _mock_response({}, status_code=401)
        )

        tool = BaiduSearchTool(api_key="baidu-test-key")
        articles = tool.search("AI")

        assert articles == []


# ─────────────────── Dispatch Integration Tests ─────────────────

class TestToolDispatch:
    """Test that _create_tool correctly dispatches to new tools."""

    def test_config_contains_new_engines(self):
        """Verify flexible_config registers up all 5 new engines."""
        from ai_news_collector_lib.config.flexible_config import FlexibleSearchConfig

        config = FlexibleSearchConfig()
        for engine in [
            "youtube",
            "github_search",
            "huggingface",
            "perplexity",
            "baidu_search",
        ]:
            assert engine in config.engines, f"Engine '{engine}' not in config"

    def test_import_all_tools(self):
        """Verify all new tools are importable from __init__.py."""
        from ai_news_collector_lib.tools import (
            YouTubeTool,
            GitHubSearchTool,
            HuggingFaceTool,
            PerplexityTool,
            BaiduSearchTool,
        )
        assert YouTubeTool is not None
        assert GitHubSearchTool is not None
        assert HuggingFaceTool is not None
        assert PerplexityTool is not None
        assert BaiduSearchTool is not None
