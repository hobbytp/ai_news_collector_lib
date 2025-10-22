"""
Unit tests for query enhancement functionality.

Tests cover:
- EnhancedQuery serialization and deserialization
- QueryEnhancer basic functionality
- Error handling
"""

import pytest
from unittest.mock import patch

from ai_news_collector_lib.models.enhanced_query import EnhancedQuery
from ai_news_collector_lib.utils.query_enhancer import (
    QueryEnhancer,
    QueryEnhancerError,
    LLMAPIError,
)


class TestEnhancedQuery:
    """Test EnhancedQuery data model."""

    def test_enhanced_query_creation(self):
        """Test creating an EnhancedQuery instance."""
        eq = EnhancedQuery(
            original="artificial intelligence",
            hackernews="AI trends",
            arxiv="machine learning arxiv",
        )
        assert eq.original == "artificial intelligence"
        assert eq.hackernews == "AI trends"

    def test_get_for_engine(self):
        """Test getting query for a specific engine."""
        eq = EnhancedQuery(
            original="test query",
            hackernews="hn variant",
            arxiv="arxiv variant",
        )

        assert eq.get_for_engine("hackernews") == "hn variant"
        assert eq.get_for_engine("arxiv") == "arxiv variant"

        # Test that unknown engine raises ValueError
        with pytest.raises(ValueError, match="Unsupported engine"):
            eq.get_for_engine("unknown_engine")

    def test_get_enabled_engines(self):
        """Test getting list of enabled engines."""
        eq = EnhancedQuery(
            original="test",
            hackernews="hn",
            arxiv=None,
            duckduckgo="ddg",
        )

        enabled = eq.get_enabled_engines()
        assert "hackernews" in enabled
        assert "duckduckgo" in enabled
        assert "arxiv" not in enabled

    def test_to_dict(self):
        """Test serializing EnhancedQuery to dictionary."""
        eq = EnhancedQuery(
            original="AI",
            hackernews="HN AI",
            duckduckgo="DDG AI",
        )

        data = eq.to_dict()
        assert data["original"] == "AI"
        assert data["hackernews"] == "HN AI"

    def test_from_dict(self):
        """Test deserializing EnhancedQuery from dictionary."""
        data = {
            "original": "machine learning",
            "hackernews": "ML HN",
            "arxiv": "ML research",
        }

        eq = EnhancedQuery.from_dict(data)
        assert eq.original == "machine learning"
        assert eq.hackernews == "ML HN"
        assert eq.arxiv == "ML research"


class TestQueryEnhancer:
    """Test QueryEnhancer class."""

    def test_enhancer_initialization(self):
        """Test QueryEnhancer initialization."""
        enhancer = QueryEnhancer(
            api_key="test-key-12345",
            provider="google-gemini",
            model="gemini-2.5-pro",
        )
        assert enhancer.api_key == "test-key-12345"
        assert enhancer.provider == "google-gemini"
        assert enhancer.model == "gemini-2.5-pro"

    def test_error_handling(self):
        """Test error exceptions."""
        with pytest.raises(QueryEnhancerError):
            raise QueryEnhancerError("test error")

        with pytest.raises(LLMAPIError):
            raise LLMAPIError("API failed")

    def test_supported_engines(self):
        """Test that SUPPORTED_ENGINES contains all 11 engines."""
        expected_engines = {
            "hackernews",
            "arxiv",
            "duckduckgo",
            "rss_feeds",
            "newsapi",
            "tavily",
            "google_search",
            "bing_search",
            "serper",
            "brave_search",
            "metasota_search",
        }

        assert set(QueryEnhancer.SUPPORTED_ENGINES) == expected_engines
        assert len(QueryEnhancer.SUPPORTED_ENGINES) == 11
