"""
工具模块
包含各种实用工具类
"""

from .content_extractor import ContentExtractor
from .keyword_extractor import KeywordExtractor
from .cache import CacheManager
from .reporter import ReportGenerator

__all__ = [
    'ContentExtractor',
    'KeywordExtractor', 
    'CacheManager',
    'ReportGenerator'
]

# 可选依赖：scheduler 依赖第三方包 `schedule`
try:
    from .scheduler import DailyScheduler
    __all__.append('DailyScheduler')
except Exception:
    # 未安装可选依赖时不导出 DailyScheduler，避免导入失败
    DailyScheduler = None
