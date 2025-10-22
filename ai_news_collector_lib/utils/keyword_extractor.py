"""
关键词提取器
用于从文本中提取关键词
"""

import re
import logging
from typing import List, Dict
from collections import Counter

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """关键词提取器"""

    def __init__(self, max_keywords: int = 10, min_word_length: int = 3):
        """
        初始化关键词提取器

        Args:
            max_keywords: 最大关键词数量
            min_word_length: 最小词长度
        """
        self.max_keywords = max_keywords
        self.min_word_length = min_word_length

        # 常见停用词
        self.stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "among",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "shall",
            "a",
            "an",
            "as",
            "are",
            "was",
            "were",
            "been",
            "being",
            "have",
            "has",
            "had",
            "having",
            "do",
            "does",
            "did",
            "doing",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "shall",
            "am",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "having",
            "do",
            "does",
            "did",
            "doing",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "shall",
        }

    def extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词

        Args:
            text: 输入文本

        Returns:
            List[str]: 关键词列表
        """
        try:
            # 清理文本
            cleaned_text = self._clean_text(text)

            # 分词
            words = self._tokenize(cleaned_text)

            # 过滤停用词和短词
            filtered_words = self._filter_words(words)

            # 统计词频
            word_count = Counter(filtered_words)

            # 获取最常见的词
            keywords = [word for word, count in word_count.most_common(self.max_keywords)]

            return keywords

        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            return []

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 转换为小写
        text = text.lower()

        # 移除特殊字符，保留字母、数字和空格
        text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

        # 移除多余的空格
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        # 简单的空格分词
        words = text.split()

        # 过滤长度
        words = [word for word in words if len(word) >= self.min_word_length]

        return words

    def _filter_words(self, words: List[str]) -> List[str]:
        """过滤单词"""
        filtered = []

        for word in words:
            # 过滤停用词
            if word in self.stop_words:
                continue

            # 过滤纯数字
            if word.isdigit():
                continue

            # 过滤太短的词
            if len(word) < self.min_word_length:
                continue

            filtered.append(word)

        return filtered

    def extract_phrases(
        self, text: str, min_phrase_length: int = 2, max_phrase_length: int = 3
    ) -> List[str]:
        """
        提取短语

        Args:
            text: 输入文本
            min_phrase_length: 最小短语长度
            max_phrase_length: 最大短语长度

        Returns:
            List[str]: 短语列表
        """
        try:
            # 清理文本
            cleaned_text = self._clean_text(text)

            # 分词
            words = self._tokenize(cleaned_text)

            # 生成n-gram短语
            phrases = []
            for n in range(min_phrase_length, max_phrase_length + 1):
                for i in range(len(words) - n + 1):
                    phrase = " ".join(words[i : i + n])
                    if len(phrase) > 0:
                        phrases.append(phrase)

            # 统计短语频率
            phrase_count = Counter(phrases)

            # 获取最常见的短语
            top_phrases = [phrase for phrase, count in phrase_count.most_common(self.max_keywords)]

            return top_phrases

        except Exception as e:
            logger.warning(f"Phrase extraction failed: {e}")
            return []

    def get_word_frequency(self, text: str) -> Dict[str, int]:
        """
        获取词频统计

        Args:
            text: 输入文本

        Returns:
            Dict[str, int]: 词频字典
        """
        try:
            # 清理文本
            cleaned_text = self._clean_text(text)

            # 分词
            words = self._tokenize(cleaned_text)

            # 过滤单词
            filtered_words = self._filter_words(words)

            # 统计词频
            word_count = Counter(filtered_words)

            return dict(word_count)

        except Exception as e:
            logger.warning(f"Word frequency analysis failed: {e}")
            return {}
