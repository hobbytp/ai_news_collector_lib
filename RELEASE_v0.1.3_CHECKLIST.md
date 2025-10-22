# v0.1.3 版本发布 - 文档更新清单

## 📋 需要更新的文档列表

### 1. **README.md** - 主文档
需要更新的位置和内容：

#### a) 第8行 - 版本徽章
```markdown
# 旧：
[![Latest Release](https://img.shields.io/badge/Latest-v0.1.2-brightgreen)]

# 新：
[![Latest Release](https://img.shields.io/badge/Latest-v0.1.3-brightgreen)]
```

#### b) 第12行 - 最新更新部分
```markdown
# 旧：
## 🚀 最新更新 (v0.1.2 - 安全版本)

# 新：
## 🚀 最新更新 (v0.1.3 - LLM 查询增强版本)
```

#### c) 第13-28行 - 更新特性描述
```markdown
# 旧：
> **这是一个关键的安全版本更新！** 建议所有用户升级。

### 🔒 安全改进
- ✅ 全面安全审计...
...

# 新：
> **这是一个功能增强版本！** 添加了AI驱动的查询优化功能。

### 🤖 LLM 查询增强
- ✅ **AI 驱动查询优化** - 使用 Google Gemini 优化搜索查询
- ✅ **单一 LLM 调用** - 一次 API 调用为所有搜索引擎生成优化查询
- ✅ **智能缓存** - 24 小时缓存减少 LLM 调用成本
- ✅ **11 个搜索引擎支持** - 为所有搜索源提供优化查询
- ✅ **优雅降级** - LLM 失败时自动回退到原始查询
- ✅ **完整测试覆盖** - 8 个单元测试，81% 代码覆盖率
```

#### d) 第402行 - 文档链接更新
```markdown
# 旧：
- [安全审计](API_KEY_SECURITY_AUDIT.md) - v0.1.2安全改进详情

# 新：
- [安全审计](API_KEY_SECURITY_AUDIT.md) - v0.1.2安全改进详情
- [LLM 查询增强](QUERY_ENHANCEMENT_GUIDE.md) - v0.1.3新功能说明
```

#### e) 第495-510行 - 更新日志部分
```markdown
# 旧：
### v0.1.2 (2025-10-21) - 🔒 安全版本
- ✅ 全面安全审计...

### v0.1.0 (2025-10-07)
- 初始预发布版本...

# 新：
### v0.1.3 (2025-10-22) - 🤖 LLM 查询增强版本
- ✅ **LLM 驱动查询优化** - Google Gemini 集成
- ✅ **单一 LLM 调用架构** - 为所有启用的搜索引擎生成优化查询
- ✅ **EnhancedQuery 数据模型** - 支持 11 个搜索引擎的查询变体
- ✅ **QueryEnhancer 类** - 完整的缓存、错误处理和降级机制
- ✅ **配置集成** - 新增 5 个配置字段
- ✅ **完整的单元测试** - 8 个测试全部通过，81% 覆盖率
- ✅ **Flake8 & Black 检查** - 代码质量通过所有检查

### v0.1.2 (2025-10-21) - 🔒 安全版本
- ✅ 全面安全审计...

### v0.1.0 (2025-10-07)
- 初始预发布版本...
```

#### f) 快速开始部分 - 添加查询增强示例
```markdown
在 "高级使用（包含内容提取和关键词提取）" 之后添加：

### LLM 查询增强使用（v0.1.3+）

```python
import asyncio
from ai_news_collector_lib import AdvancedAINewsCollector, AdvancedSearchConfig

async def main():
    # 创建配置 - 启用 LLM 查询增强
    config = AdvancedSearchConfig(
        enable_query_enhancement=True,          # 启用查询增强
        llm_api_key="your-google-api-key",    # 从 GOOGLE_API_KEY 环境变量自动读取
        enable_hackernews=True,
        enable_arxiv=True,
        enable_duckduckgo=True,
        max_articles_per_source=10
    )
    
    # 创建收集器
    collector = AdvancedAINewsCollector(config)
    
    # 收集新闻 - 自动使用 LLM 优化查询
    result = await collector.collect_news_advanced("machine learning safety")
    
    # 查看优化后的查询
    for engine, enhanced_query in result.enhanced_queries.items():
        print(f"{engine}: {enhanced_query}")
    
    return result

asyncio.run(main())
```
```

### 2. **pyproject.toml** - 版本配置
需要更新的位置：

#### 第7行 - 版本号
```toml
# 旧：
version = "0.1.2"

# 新：
version = "0.1.3"
```

#### 第46行附近 - 依赖更新
```toml
# 在 dependencies 中添加：
dependencies = [
    "requests>=2.28.0",
    "beautifulsoup4>=4.11.0",
    "feedparser>=6.0.0",
    "python-dotenv>=0.19.0",
    "google-generativeai>=0.3.0",  # 新增
]
```

### 3. **setup.py** - 安装脚本
需要更新的位置：

#### 第32行 - 版本号
```python
# 旧：
version="0.1.2",

# 新：
version="0.1.3",
```

#### dependencies 部分 - 添加 google-generativeai
```python
# 在 install_requires 中添加：
'google-generativeai>=0.3.0',
```

### 4. **USAGE_GUIDE.md** - 使用指南（如果存在）
- 添加"LLM 查询增强"部分
- 说明如何启用和配置查询增强功能
- 提供使用示例

### 5. **CHANGELOG.md** 或 **HISTORY.md**（如果存在）
- 添加 v0.1.3 的详细变更记录
- 包括新增功能、改进、修复的内容

### 6. **openspec/changes/add-query-enhancement-llm/** - OpenSpec 规范

创建或更新以下文件：
- `proposal.md` - 变更提案
- `tasks.md` - 任务列表
- `design.md` - 设计文档
- 相关的 spec delta 文件

## 📝 v0.1.3 发布说明模板

### 发布摘要
```
v0.1.3 - LLM 查询增强版本 (2025-10-22)

这个版本引入了 AI 驱动的查询优化功能，利用 Google Gemini LLM 自动为所有搜索引擎生成优化的查询变体。

关键改进：
- 🤖 LLM 驱动的查询优化（Google Gemini 集成）
- ⚡ 单一 API 调用架构（一次调用为所有引擎生成优化查询）
- 💾 智能缓存机制（24 小时 TTL）
- 🎯 支持所有 11 个搜索引擎
- 🛡️ 完整的错误处理和优雅降级
- ✅ 全面的单元测试覆盖

新增依赖：
- google-generativeai>=0.3.0

文档更新：
- README.md - 新增查询增强使用示例
- IMPLEMENTATION_SUMMARY.md - 实现总结
- IMPLEMENTATION_CHECKLIST.md - 完成清单
```

### GitHub Release 模板
```markdown
## 🤖 LLM 驱动的查询增强

### ✨ 新特性

- **AI 查询优化** - 使用 Google Gemini 自动优化搜索查询
- **单一 LLM 调用** - 一次 API 调用为所有启用的搜索引擎生成优化查询
- **智能缓存** - 基于原始查询的缓存，24 小时 TTL，独立于启用的引擎配置
- **完整的搜索引擎支持** - HackerNews, ArXiv, DuckDuckGo, RSS Feeds, NewsAPI, Tavily, Google Search, Bing Search, Serper, Brave Search, Metasota Search
- **优雅降级** - LLM 失败时自动返回原始查询
- **完整测试** - 8 个单元测试，81% 代码覆盖率

### 📦 新增依赖

- `google-generativeai>=0.3.0` (v0.8.5 已测试)

### 🚀 快速开始

```python
from ai_news_collector_lib import AdvancedAINewsCollector, AdvancedSearchConfig

config = AdvancedSearchConfig(
    enable_query_enhancement=True,
    enable_hackernews=True,
    enable_arxiv=True
)

collector = AdvancedAINewsCollector(config)
result = await collector.collect_news_advanced("AI safety")
print(result.enhanced_queries)  # 查看优化后的查询
```

### 📚 文档

- [LLM 查询增强实现总结](IMPLEMENTATION_SUMMARY.md)
- [完成清单](IMPLEMENTATION_CHECKLIST.md)

### 🧪 测试

所有测试通过：
- ✅ 8 个单元测试
- ✅ 20 个集成测试  
- ✅ 81% 代码覆盖率

### 🔧 升级指南

1. 更新 package：`pip install --upgrade ai-news-collector-lib==0.1.3`
2. 可选：设置 GOOGLE_API_KEY 环境变量用于查询增强
3. 在配置中设置 `enable_query_enhancement=True` 启用功能

### 致谢

特别感谢所有为此版本贡献代码和反馈的人员！
```

## ✅ 发布前检查清单

- [ ] 更新 README.md（版本号、新特性、使用示例）
- [ ] 更新 pyproject.toml（版本号、依赖）
- [ ] 更新 setup.py（版本号、依赖）
- [ ] 创建/更新 CHANGELOG.md
- [ ] 创建 GitHub Release 草稿
- [ ] 验证所有测试通过
- [ ] 验证 flake8/black 检查通过
- [ ] 创建 git tag: v0.1.3
- [ ] 推送到 GitHub（触发 CI/CD）
- [ ] 监控 PyPI 发布过程

## 📌 注意事项

1. **向后兼容性** - v0.1.3 与之前版本完全向后兼容
2. **可选功能** - LLM 查询增强是可选的，不启用不会影响现有功能
3. **API 密钥** - 需要 Google Gemini API 密钥才能使用查询增强功能
4. **缓存** - 缓存是可选的，可通过配置禁用

---

**建议的发布流程**：
1. 更新所有文档
2. 创建 git branch: `release/v0.1.3`
3. 提交更改
4. 创建 Pull Request 进行最终审查
5. 合并到 master
6. 创建 git tag: v0.1.3
7. 推送 tag（自动触发 PyPI 发布）
