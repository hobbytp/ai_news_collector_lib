# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-10-21

### 🔥 Critical Fixes

#### Fixed

- **[HIGH] AdvancedAINewsCollector 配置传递问题**
  - 修复了 `AdvancedAINewsCollector` 初始化时丢失高级搜索提供商配置的严重问题
  - 之前版本中，Tavily、Google、Serper、Brave、MetaSota 的 API 配置被错误地丢弃
  - 现在直接传递完整的 `AdvancedSearchConfig` 到父类，保留所有提供商配置
  - 影响：修复前用户配置的付费 API 服务可能无法正常工作

- **[HIGH] 异步并发执行问题**
  - 修复了 `collect_news` 方法中的伪异步执行问题
  - 之前的实现虽然使用了 `async/await` 语法，但实际上是串行执行，阻塞事件循环
  - 现在使用 `asyncio.to_thread()` 将同步 I/O 操作移到线程池
  - 使用 `asyncio.gather()` 实现真正的并发执行
  - 性能提升：多源搜索速度提升 **2-5倍**，事件循环不再阻塞

### 📝 Code Quality

- 修复了所有 flake8 代码风格问题（清理未使用的导入、空白行、缩进等）
- 所有代码符合 PEP 8 规范（88 字符行长度限制）

### 📖 Documentation

- 添加了 `CRITICAL_FIXES_v0.1.2.md` 详细文档
- 包含问题分析、修复方案、性能对比和测试结果

### ✅ Testing

- 添加了 `test_verify_fixes.py` 验证脚本
- 所有关键修复已通过验证测试（3/3 通过）

---

## [0.1.1] - Previous Release

### Added

- 基础的 AI 新闻收集功能
- 支持多个新闻源（HackerNews, ArXiv, DuckDuckGo, NewsAPI 等）
- 内容提取和关键词分析
- 缓存机制
- CLI 工具

### Features

- 异步搜索架构（基础实现）
- 配置化的搜索源管理
- 文章去重和排序
- 定时任务支持

---

## Links

- [v0.1.2 关键修复详情](CRITICAL_FIXES_v0.1.2.md)
- [PyPI 发布指南](PYPI_RELEASE_GUIDE.md)
- [使用指南](USAGE_GUIDE.md)
