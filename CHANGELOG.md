# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6] - 2026-03-17

### ✨ Added

- **Baidu Search 集成**
  - 新增 `BaiduSearchTool`，接入百度千帆 `POST /v2/ai_search/web_search`
  - 支持 `messages`、`search_source=baidu_search_v2`、网页模态 `resource_type_filter`
  - 新增 API 级日期过滤：`search_filter.range.page_time`（按 `days_back` 生成）
  - 新增客户端 UTC 兜底过滤，确保返回时间范围一致

- **配置层支持**
  - `SearchConfig` 新增 `enable_baidu_search`、`baidu_search_api_key`
  - 自动读取环境变量 `BAIDU_SEARCH_API_KEY` 并自动启用源
  - `FlexibleSearchConfig` 新增 `baidu_search` 默认引擎和 env 映射
  - `APIKeyManager` 新增 `baidu_search` key 读取、状态查询和服务信息

- **收集器与导出**
  - `AINewsCollector`、`FlexibleAINewsCollector` 新增百度引擎初始化逻辑
  - `tools.__init__` 新增 `BaiduSearchTool` 导出
  - `EnhancedQuery` 与 `QueryEnhancer.SUPPORTED_ENGINES` 新增 `baidu_search`

### 🧪 Testing

- 新增 `TestBaiduSearchTool` 单元测试（成功/空响应/API错误）
- 更新工具注册与引擎数量断言（含 `baidu_search`）
- 关键用例验证通过：`43 passed`

## [0.1.4] - 2025-10-29

### 🎯 Major Feature: Time Filtering Enhancement

#### Added

- **Comprehensive Time Filtering System**
  - 实现了所有搜索引擎的时间过滤功能
  - 支持API级别和客户端双重过滤机制
  - 时间过滤准确率从0%提升到100%

- **API-Level Time Filtering**
  - **Brave Search API**: 添加`freshness`参数支持（pd/pw/pm/py）
  - **Tavily API**: 添加`time_range`和`days`参数支持
  - **NewsAPI**: 确认`from`和`to`参数正确实现
  - **Google Search API**: 保持现有`dateRestrict`参数功能

- **Client-Side Time Filtering**
  - 为所有搜索引擎添加统一的`_filter_by_date`方法
  - 智能时间格式解析（支持ISO、Z结尾等多种格式）
  - 优雅的错误处理和降级机制
  - ⏰ **统一UTC时区处理**：所有时间过滤以UTC为准，所有`published`字段输出为ISO8601(UTC)格式
  - ⏰ **Naive时间自动处理**：自动将无时区信息的时间视为UTC

- **Enhanced Date Extraction**
  - 为每个搜索引擎添加专门的`_extract_published_time`方法
  - 支持多种时间字段的自动识别和解析
  - 统一的时间处理接口

#### Fixed

- **Time Filtering Issues**
  - 修复了8个搜索引擎的时间过滤问题
  - 解决了用户设置1天搜索却返回很久之前文章的问题
  - 确保所有返回的文章都在指定时间范围内

- **Search Engine Specific Fixes**
  - **SerperTool**: 添加客户端时间过滤
  - **BraveSearchTool**: 添加API和客户端双重过滤
  - **MetaSotaSearchTool**: 优化时间提取和客户端过滤
  - **TavilyTool**: 添加API和客户端双重过滤
  - **HackerNewsTool**: 添加客户端时间过滤 + UNIX时间戳转UTC（使用`datetime.fromtimestamp(..., tz=timezone.utc)`）
  - **ArxivTool**: 优化时间提取逻辑
  - **DuckDuckGoTool**: 添加客户端时间过滤
  - **NewsAPITool**: 添加客户端备用过滤

#### Testing

- **New Test Suite**: `tests/test_date_filtering.py`
  - 专门的时间过滤功能测试
  - 覆盖所有搜索引擎的时间过滤验证
  - 集成测试和不同时间范围测试
  - 100%时间过滤准确率验证

- **Diagnostic Tools**
  - `debug_date_filtering.py`: 时间过滤问题诊断工具
  - `test_date_filtering_fixed.py`: 修复效果验证工具

#### Documentation

- **Comprehensive Documentation**: `DATE_FILTERING_FIX_SUMMARY.md`
  - 详细的问题分析和修复方案
  - 基于Context7 API文档的精确修复
  - 完整的测试结果和性能对比
  - 使用说明和后续建议

### 📊 Performance Improvements

- **Time Filtering Accuracy**: 0% → 100% ✅
- **Problematic Search Engines**: 8 → 0 ✅
- **Articles Outside Time Range**: Many → 0 ✅
- **Dual Filtering Mechanism**: API + Client-side backup
- **Smart Date Extraction**: Multi-format support

### 🔧 Technical Details

- **Unified Interface**: 所有搜索引擎使用相同的`_filter_by_date`方法
- **Error Handling**: 时间解析失败时的优雅降级
- **Code Maintainability**: 清晰的方法分离和注释
- **User Experience**: 精确的时间控制，一致的行为

---

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
