"""
缓存管理器
提供结果缓存功能
"""

import json
import os
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = "./cache", default_ttl_hours: int = 24):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            default_ttl_hours: 默认TTL（小时）
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl_hours = default_ttl_hours
        
        # 创建缓存目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Cache manager initialized with directory: {self.cache_dir}")
    
    def get_cache_key(self, query: str, sources: list, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            query: 搜索查询
            sources: 搜索源列表
            **kwargs: 其他参数
            
        Returns:
            str: 缓存键
        """
        # 构建缓存数据
        cache_data = {
            'query': query,
            'sources': sorted(sources),
            **kwargs
        }
        
        # 生成MD5哈希
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存结果
        
        Args:
            cache_key: 缓存键
            
        Returns:
            Optional[Dict]: 缓存结果，如果不存在或过期则返回None
        """
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            if not cache_file.exists():
                return None
            
            # 读取缓存文件
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # 检查是否过期
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            ttl_hours = cached_data.get('ttl_hours', self.default_ttl_hours)
            
            if datetime.now() - cache_time > timedelta(hours=ttl_hours):
                # 缓存过期，删除文件
                cache_file.unlink()
                logger.debug(f"Cache expired for key: {cache_key}")
                return None
            
            logger.debug(f"Cache hit for key: {cache_key}")
            return cached_data['result']
            
        except Exception as e:
            logger.warning(f"Cache read failed for key {cache_key}: {e}")
            return None
    
    def cache_result(self, cache_key: str, result: Dict[str, Any], ttl_hours: Optional[int] = None):
        """
        缓存结果
        
        Args:
            cache_key: 缓存键
            result: 结果数据
            ttl_hours: TTL（小时），None使用默认值
        """
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # 准备缓存数据
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'ttl_hours': ttl_hours or self.default_ttl_hours,
                'result': result
            }
            
            # 写入缓存文件
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Result cached with key: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Cache write failed for key {cache_key}: {e}")
    
    def clear_cache(self, older_than_hours: Optional[int] = None):
        """
        清理缓存
        
        Args:
            older_than_hours: 清理多少小时前的缓存，None清理所有
        """
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            removed_count = 0
            
            for cache_file in cache_files:
                try:
                    # 读取文件时间戳
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    cache_time = datetime.fromisoformat(cached_data['timestamp'])
                    
                    # 检查是否需要删除
                    should_remove = False
                    if older_than_hours is None:
                        should_remove = True
                    else:
                        if datetime.now() - cache_time > timedelta(hours=older_than_hours):
                            should_remove = True
                    
                    if should_remove:
                        cache_file.unlink()
                        removed_count += 1
                        
                except Exception as e:
                    logger.warning(f"Error processing cache file {cache_file}: {e}")
                    # 如果文件损坏，也删除
                    cache_file.unlink()
                    removed_count += 1
            
            logger.info(f"Cache cleanup completed: {removed_count} files removed")
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Returns:
            Dict: 缓存信息
        """
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            
            total_files = len(cache_files)
            total_size = sum(f.stat().st_size for f in cache_files)
            
            # 统计过期文件
            expired_files = 0
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    cache_time = datetime.fromisoformat(cached_data['timestamp'])
                    ttl_hours = cached_data.get('ttl_hours', self.default_ttl_hours)
                    
                    if datetime.now() - cache_time > timedelta(hours=ttl_hours):
                        expired_files += 1
                        
                except Exception:
                    expired_files += 1
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'expired_files': expired_files,
                'cache_dir': str(self.cache_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'expired_files': 0,
                'cache_dir': str(self.cache_dir),
                'error': str(e)
            }
    
    def is_cached(self, cache_key: str) -> bool:
        """
        检查是否已缓存
        
        Args:
            cache_key: 缓存键
            
        Returns:
            bool: 是否已缓存且未过期
        """
        return self.get_cached_result(cache_key) is not None
