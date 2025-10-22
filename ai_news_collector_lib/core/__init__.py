"""
核心模块
包含主要的搜集器类
"""

from .collector import AINewsCollector
from .advanced_collector import AdvancedAINewsCollector

__all__ = ["AINewsCollector", "AdvancedAINewsCollector"]
