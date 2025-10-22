"""
定时任务调度器
提供定时执行新闻收集的功能
"""

import asyncio
import logging
import time
from typing import Callable, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

try:
    import schedule
except ImportError:
    schedule = None

logger = logging.getLogger(__name__)


class DailyScheduler:
    """每日调度器"""

    def __init__(
        self,
        collector_func: Callable,
        schedule_time: str = "09:00",
        timezone: str = "Asia/Shanghai",
    ):
        """
        初始化调度器

        Args:
            collector_func: 收集函数
            schedule_time: 调度时间
            timezone: 时区

        Raises:
            ImportError: 如果 schedule 模块未安装
        """
        if schedule is None:
            raise ImportError(
                "The 'schedule' package is required to use DailyScheduler. "
                "Install it with: pip install schedule"
            )

        self.collector_func = collector_func
        self.schedule_time = schedule_time
        self.timezone = timezone
        self.is_running = False

        # 设置定时任务
        schedule.every().day.at(schedule_time).do(self._run_collection)

        logger.info(f"Scheduler initialized: {schedule_time} {timezone}")

    def _run_collection(self):
        """运行收集任务"""
        try:
            logger.info(f"Starting scheduled collection at {datetime.now()}")

            # 运行收集函数
            if asyncio.iscoroutinefunction(self.collector_func):
                asyncio.run(self.collector_func())
            else:
                self.collector_func()

            logger.info("Scheduled collection completed successfully")

        except Exception as e:
            logger.error(f"Scheduled collection failed: {e}")

    def start(self):
        """启动调度器"""
        self.is_running = True
        logger.info("Scheduler started")

        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

    def stop(self):
        """停止调度器"""
        self.is_running = False
        logger.info("Scheduler stopped")

    def run_once(self):
        """立即运行一次收集"""
        self._run_collection()

    def get_next_run_time(self) -> Optional[datetime]:
        """获取下次运行时间"""
        try:
            next_run = schedule.next_run()
            if next_run:
                return next_run
        except Exception as e:
            logger.warning(f"Failed to get next run time: {e}")
        return None

    def get_schedule_info(self) -> Dict[str, Any]:
        """获取调度信息"""
        return {
            "schedule_time": self.schedule_time,
            "timezone": self.timezone,
            "is_running": self.is_running,
            "next_run": self.get_next_run_time(),
        }


class AdvancedScheduler:
    """高级调度器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化高级调度器

        Args:
            config: 配置字典
        """
        self.config = config
        self.schedulers = {}
        self.is_running = False

        # 初始化多个调度器
        self._initialize_schedulers()

        logger.info("Advanced scheduler initialized")

    def _initialize_schedulers(self):
        """初始化调度器"""
        schedules = self.config.get("schedules", [])

        for schedule_config in schedules:
            name = schedule_config.get("name", "default")
            time = schedule_config.get("time", "09:00")
            func = schedule_config.get("function")

            if func:
                scheduler = DailyScheduler(func, time)
                self.schedulers[name] = scheduler
                logger.info(f"Scheduler '{name}' initialized for {time}")

    def start_all(self):
        """启动所有调度器"""
        self.is_running = True

        # 启动所有调度器
        for name, scheduler in self.schedulers.items():
            scheduler.start()
            logger.info(f"Scheduler '{name}' started")

    def stop_all(self):
        """停止所有调度器"""
        self.is_running = False

        for name, scheduler in self.schedulers.items():
            scheduler.stop()
            logger.info(f"Scheduler '{name}' stopped")

    def run_scheduler(self, name: str):
        """运行指定调度器"""
        if name in self.schedulers:
            self.schedulers[name].run_once()
        else:
            logger.warning(f"Scheduler '{name}' not found")

    def get_all_schedules_info(self) -> Dict[str, Any]:
        """获取所有调度信息"""
        info = {}
        for name, scheduler in self.schedulers.items():
            info[name] = scheduler.get_schedule_info()
        return info
