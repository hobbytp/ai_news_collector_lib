"""
Query Enhancer - LLM-based Query Optimization

This module provides the QueryEnhancer class that uses Google Gemini 2.5 Pro LLM
to optimize user queries for better search results across all supported search engines.

Key Features:
- Single LLM call per user query (generates variants for all enabled engines)
- Intelligent caching based on original query hash
- Graceful fallback to original query on LLM failure
- Support for all 11 search engines (4 free + 7 API-based)
- Comprehensive error handling and logging
"""

import hashlib
import json
import logging
import os
import time
from typing import Dict, List, Optional
import asyncio

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from ai_news_collector_lib.models import EnhancedQuery


logger = logging.getLogger(__name__)


class QueryEnhancerError(Exception):
    """Base exception for QueryEnhancer errors."""

    pass


class LLMAPIError(QueryEnhancerError):
    """Exception raised when LLM API call fails."""

    pass


class CacheError(QueryEnhancerError):
    """Exception raised when cache operations fail."""

    pass


class QueryEnhancer:
    """
    Optimizes user queries using Google Gemini 2.5 Pro LLM.

    This class:
    1. Takes a user query and list of enabled search engines
    2. Makes ONE LLM API call to generate optimized variants for all enabled engines
    3. Caches results based on the original query (cache independent of enabled engines)
    4. Returns EnhancedQuery with optimized variants for each engine

    Architecture:
    - Single LLM call: Original query + enabled engines → LLM → Variants for all engines
    - Cache key: hash(original_query) only
    - Cache value: EnhancedQuery with all engine variants
    - Performance: One LLM call cost, regardless of engine count

    Supported Engines (11 total):
    - Free (4): hackernews, arxiv, duckduckgo, rss_feeds
    - API-based (7): newsapi, tavily, google_search, bing_search, serper,
      brave_search, metasota_search
    """

    # LLM Configuration
    DEFAULT_LLM_PROVIDER = "google-gemini"
    DEFAULT_LLM_MODEL = "gemini-2.5-pro"
    DEFAULT_CACHE_TTL = 24 * 60 * 60  # 24 hours

    # Supported search engines
    SUPPORTED_ENGINES = [
        # Free engines
        "hackernews",
        "arxiv",
        "duckduckgo",
        "rss_feeds",
        # API-based engines
        "newsapi",
        "tavily",
        "google_search",
        "bing_search",
        "serper",
        "brave_search",
        "metasota_search",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = DEFAULT_LLM_PROVIDER,
        model: str = DEFAULT_LLM_MODEL,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        enable_caching: bool = True,
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize the QueryEnhancer.

        Args:
            api_key (Optional[str]): Google Gemini API key. If None, uses GOOGLE_API_KEY env var.
            provider (str): LLM provider name (currently only "google-gemini" supported)
            model (str): LLM model name (default: "gemini-2.5-pro")
            cache_ttl (int): Cache time-to-live in seconds (default: 24 hours)
            enable_caching (bool): Whether to enable result caching (default: True)
            cache_dir (Optional[str]): Directory for cache files. If None, uses in-memory cache.

        Raises:
            QueryEnhancerError: If google-generativeai is not installed
        """
        if genai is None:
            raise QueryEnhancerError(
                "google-generativeai is required for QueryEnhancer. "
                "Install it with: pip install google-generativeai>=0.3.0"
            )

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.provider = provider
        self.model = model
        self.cache_ttl = cache_ttl
        self.enable_caching = enable_caching
        self.cache_dir = cache_dir

        # In-memory cache: dict[cache_key] = (EnhancedQuery, timestamp)
        self._memory_cache: Dict[str, tuple] = {}

        # Initialize LLM
        if self.provider == "google-gemini":
            if self.api_key:
                genai.configure(api_key=self.api_key)
            self.llm_model = genai.GenerativeModel(self.model)
        else:
            raise QueryEnhancerError(f"Unsupported LLM provider: {self.provider}")

        logger.info(
            f"QueryEnhancer initialized with {self.provider}/{self.model}, "
            f"cache_ttl={self.cache_ttl}s, caching={'enabled' if enable_caching else 'disabled'}"
        )

    def _get_cache_key(self, original_query: str) -> str:
        """
        Generate cache key based on original query hash.

        Cache key is independent of enabled engines - same query → same cache key.
        Different engine configurations use the same cached result.

        Args:
            original_query (str): The original user query

        Returns:
            str: SHA256 hash of the original query
        """
        return hashlib.sha256(original_query.encode("utf-8")).hexdigest()

    def _is_cache_valid(self, timestamp: float) -> bool:
        """
        Check if cached result is still valid (not expired).

        Args:
            timestamp (float): Unix timestamp of cache entry

        Returns:
            bool: True if cache is still valid, False if expired
        """
        age = time.time() - timestamp
        return age < self.cache_ttl

    def _get_from_memory_cache(self, cache_key: str) -> Optional[EnhancedQuery]:
        """
        Retrieve result from in-memory cache if valid.

        Args:
            cache_key (str): Cache key from _get_cache_key()

        Returns:
            Optional[EnhancedQuery]: Cached query if valid, None otherwise
        """
        if cache_key not in self._memory_cache:
            return None

        cached_query, timestamp = self._memory_cache[cache_key]
        if not self._is_cache_valid(timestamp):
            del self._memory_cache[cache_key]
            return None

        logger.debug(f"Cache hit for key {cache_key[:8]}...")
        return cached_query

    def _save_to_memory_cache(self, cache_key: str, enhanced_query: EnhancedQuery) -> None:
        """
        Save result to in-memory cache.

        Args:
            cache_key (str): Cache key from _get_cache_key()
            enhanced_query (EnhancedQuery): The enhanced query result
        """
        self._memory_cache[cache_key] = (enhanced_query, time.time())
        logger.debug(f"Cached result for key {cache_key[:8]}...")

    def _build_prompt(self, original_query: str, enabled_engines: List[str]) -> str:  # noqa: E501
        """
        Build the LLM prompt for query optimization.

        The prompt instructs the LLM to:
        1. Generate optimized query variants for EACH enabled engine
        2. Return results ONLY for enabled engines (not all 11)
        3. Format as JSON with engine names as keys

        Args:
            original_query (str): The original user query
            enabled_engines (List[str]): List of enabled search engine names

        Returns:
            str: The formatted prompt for LLM
        """
        engines_str = ", ".join(enabled_engines)

        # noqa: E501 (long lines in docstring below are intentional for LLM prompt clarity)
        prompt = f"""You are an expert search query optimization specialist. Your task is to optimize a user's search query for different search engines.

Given the original query, generate optimized variants for EACH of the enabled search engines listed below.

Original Query: "{original_query}"

Enabled Search Engines: {engines_str}

For each enabled engine, create an optimized query variant that:
1. Improves search relevance and result quality
2. Uses engine-specific search syntax if beneficial (e.g., boolean operators, site:, filetype:)
3. Preserves the core intent of the original query
4. Adapts to the engine's strengths (e.g., academic focus for arxiv, news focus for newsapi)

Return ONLY a valid JSON object with the following structure:
- One key for each enabled engine
- Each value is the optimized query string
- Include ONLY the enabled engines listed above
- Do not include any other fields or explanations

Example format (for illustration only):
{{
  "arxiv": "deep learning neural networks classification",
  "google_search": "best deep learning frameworks 2024",
  "hackernews": "HN: machine learning breakthroughs"
}}

Now generate the optimized queries for the enabled engines: {engines_str}

Return ONLY valid JSON, no additional text or explanations:
"""
        return prompt

    def _parse_response(self, llm_response: str, enabled_engines: List[str]) -> Dict[str, str]:
        """
        Parse LLM response and extract optimized queries.

        Args:
            llm_response (str): Raw response from LLM
            enabled_engines (List[str]): Expected enabled engines

        Returns:
            Dict[str, str]: Mapping of engine names to optimized queries

        Raises:
            LLMAPIError: If response cannot be parsed as valid JSON
        """
        try:
            # Try to extract JSON from response
            # LLM might include extra text, so find JSON block
            response_text = llm_response.strip()

            # Try direct JSON parsing first
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx == -1 or end_idx == 0:
                    raise LLMAPIError(f"Could not find JSON in LLM response: {response_text[:200]}")
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)

            if not isinstance(result, dict):
                raise LLMAPIError(f"LLM response is not a JSON object: {type(result)}")

            # Validate that all values are strings
            for engine, query in result.items():
                if not isinstance(query, str):
                    raise LLMAPIError(f"Invalid query type for engine '{engine}': {type(query)}")

            # Log the parsed result
            logger.debug(f"Parsed LLM response with engines: {list(result.keys())}")

            return result

        except json.JSONDecodeError as e:
            raise LLMAPIError(f"Failed to parse LLM response as JSON: {e}")

    def _call_llm(self, original_query: str, enabled_engines: List[str]) -> Dict[str, str]:
        """
        Make a single LLM API call to generate optimized queries for all enabled engines.

        Args:
            original_query (str): The original user query
            enabled_engines (List[str]): List of enabled search engine names

        Returns:
            Dict[str, str]: Mapping of engine names to optimized queries

        Raises:
            LLMAPIError: If LLM API call fails
        """
        try:
            prompt = self._build_prompt(original_query, enabled_engines)

            logger.debug(
                f"Calling LLM ({self.provider}/{self.model}) with "
                f"{len(enabled_engines)} enabled engines"
            )

            # Make single LLM API call
            response = self.llm_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Low temperature for consistent results
                    max_output_tokens=2000,
                    top_p=0.95,
                ),
            )

            if not response or not response.text:
                raise LLMAPIError("Empty response from LLM")

            # Parse and return optimized queries
            return self._parse_response(response.text, enabled_engines)

        except genai.types.BlockedPromptException as e:
            raise LLMAPIError(f"LLM blocked the prompt: {e}")
        except genai.types.StopCandidateException as e:
            raise LLMAPIError(f"LLM stopped generation: {e}")
        except Exception as e:
            raise LLMAPIError(f"LLM API call failed: {e}")

    def enhance_query(
        self,
        original_query: str,
        enabled_engines: Optional[List[str]] = None,
        use_cache: Optional[bool] = None,
    ) -> EnhancedQuery:
        """
        Enhance a user query for multiple search engines.

        Architecture:
        1. Check cache using hash(original_query)
        2. If cached result is valid, return it
        3. If not cached or expired, call LLM once
        4. LLM generates optimized variants for ALL enabled engines
        5. Cache the result (independent of which engines were requested)
        6. Extract and return variants for requested engines

        Args:
            original_query (str): The original user query
            enabled_engines (Optional[List[str]]): List of engine names to optimize for.
                                                   If None, optimizes for all supported engines.
            use_cache (Optional[bool]): Override caching setting (True/False/None=use default)

        Returns:
            EnhancedQuery: Object containing original query and optimized variants

        Example:
            >>> enhancer = QueryEnhancer(api_key="your-key")
            >>> result = enhancer.enhance_query(
            ...     original_query="machine learning safety",
            ...     enabled_engines=["arxiv", "google_search", "hackernews"]
            ... )
            >>> print(result.arxiv)  # Optimized for arxiv
            >>> print(result.google_search)  # Optimized for google_search
        """
        # Validate and normalize enabled_engines
        if enabled_engines is None:
            enabled_engines = self.SUPPORTED_ENGINES
        else:
            enabled_engines = list(set(enabled_engines))  # Remove duplicates
            for engine in enabled_engines:
                if engine not in self.SUPPORTED_ENGINES:
                    raise QueryEnhancerError(f"Unsupported engine: {engine}")

        # Determine cache setting
        use_cache_setting = use_cache if use_cache is not None else self.enable_caching

        # Get cache key (independent of enabled_engines)
        cache_key = self._get_cache_key(original_query)

        # Try to get from cache
        if use_cache_setting:
            cached = self._get_from_memory_cache(cache_key)
            if cached is not None:
                return cached

        # Cache miss or caching disabled - call LLM
        logger.info(
            f"Enhancing query (engines={len(enabled_engines)}): " f"'{original_query[:50]}...'"
        )

        try:
            # Single LLM call for all enabled engines
            optimized_dict = self._call_llm(original_query, enabled_engines)

            # Create EnhancedQuery with original + all optimized variants
            enhanced = EnhancedQuery(original=original_query)
            for engine, query in optimized_dict.items():
                if engine in self.SUPPORTED_ENGINES:
                    enhanced.set_for_engine(engine, query)

            # Save to cache
            if use_cache_setting:
                self._save_to_memory_cache(cache_key, enhanced)

            logger.info(f"Successfully enhanced query for {enhanced.get_engine_count()} engines")
            return enhanced

        except LLMAPIError as e:
            logger.warning(f"LLM enhancement failed: {e}. Using original query as fallback.")
            # Graceful fallback: return original query unchanged
            return EnhancedQuery(original=original_query)
        except Exception as e:
            logger.error(f"Unexpected error in enhance_query: {e}", exc_info=True)
            # Graceful fallback
            return EnhancedQuery(original=original_query)

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._memory_cache.clear()
        logger.info("Cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dict[str, int]: Dictionary with 'entries' count
        """
        return {
            "entries": len(self._memory_cache),
            "cache_ttl": self.cache_ttl,
        }


async def enhance_query_async(
    enhancer: QueryEnhancer,
    original_query: str,
    enabled_engines: Optional[List[str]] = None,
) -> EnhancedQuery:
    """
    Asynchronous wrapper for query enhancement.

    This function runs the blocking enhance_query() in a thread pool,
    allowing it to be used in async contexts without blocking the event loop.

    Args:
        enhancer (QueryEnhancer): The QueryEnhancer instance
        original_query (str): The original user query
        enabled_engines (Optional[List[str]]): List of enabled engines

    Returns:
        EnhancedQuery: Enhanced query with optimized variants
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: enhancer.enhance_query(original_query, enabled_engines)
    )
