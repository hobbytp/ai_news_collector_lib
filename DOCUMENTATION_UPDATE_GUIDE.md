# v0.1.3 发布 - 文档更新对比

## 1. README.md 更新

### 版本徽章 (第8行)
```diff
- [![Latest Release](https://img.shields.io/badge/Latest-v0.1.2-brightgreen)](https://github.com/ai-news-collector/ai-news-collector-lib/releases/tag/v0.1.2)
+ [![Latest Release](https://img.shields.io/badge/Latest-v0.1.3-brightgreen)](https://github.com/ai-news-collector/ai-news-collector-lib/releases/tag/v0.1.3)
```

### 最新更新部分 (第12行)
```diff
- ## 🚀 最新更新 (v0.1.2 - 安全版本)
+ ## 🚀 最新更新 (v0.1.3 - LLM 查询增强版本)

- > **这是一个关键的安全版本更新！** 建议所有用户升级。
+ > **这是一个功能增强版本！** 添加了 AI 驱动的查询优化功能。

- ### 🔒 安全改进
+ ### 🤖 LLM 查询增强
- - ✅ **全面安全审计** - 清理VCR测试cassettes中的所有敏感数据
+ - ✅ **AI 驱动查询优化** - 使用 Google Gemini LLM 优化搜索查询
- - ✅ **凭证管理改进** - 将所有测试API密钥替换为"FILTERED"占位符
+ - ✅ **单一 LLM 调用** - 一次 API 调用为所有启用的搜索引擎生成优化查询
- - ✅ **端点校验** - 更新所有测试cassette的URL为真实API端点
+ - ✅ **智能缓存** - 24 小时缓存减少 LLM 调用成本
- - ✅ **无凭证泄露** - 确保测试数据中不包含任何有效凭证
+ - ✅ **11 个搜索引擎** - 为所有搜索源提供优化查询
+ - ✅ **优雅降级** - LLM 失败时自动回退到原始查询
```

### 更新日志 (第495行)
```diff
+ ### v0.1.3 (2025-10-22) - 🤖 LLM 查询增强版本
+ - ✅ **LLM 驱动查询优化** - Google Gemini 集成
+ - ✅ **单一 LLM 调用架构** - 为所有启用的搜索引擎生成优化查询
+ - ✅ **EnhancedQuery 数据模型** - 支持 11 个搜索引擎的查询变体
+ - ✅ **QueryEnhancer 类** - 完整的缓存、错误处理和降级机制
+ - ✅ **配置集成** - 新增 5 个配置字段
+ - ✅ **完整的单元测试** - 8 个测试全部通过，81% 覆盖率
+ - ✅ **Flake8 & Black 检查** - 代码质量通过所有检查
+
  ### v0.1.2 (2025-10-21) - 🔒 安全版本
```

### 新增快速开始示例
在"高级使用"部分之后添加新的"LLM 查询增强使用"小节

## 2. pyproject.toml 更新

### 版本号 (第7行)
```diff
- version = "0.1.2"
+ version = "0.1.3"
```

### 依赖 (第41-45行)
```diff
  dependencies = [
      "requests>=2.28.0",
      "beautifulsoup4>=4.11.0",
      "feedparser>=6.0.0",
      "python-dotenv>=0.19.0",
+     "google-generativeai>=0.3.0",
  ]
```

## 3. setup.py 更新

### 版本号 (第32行)
```diff
- version="0.1.2",
+ version="0.1.3",
```

### 依赖 (install_requires 中)
```diff
  install_requires=[
      'requests>=2.28.0',
      'beautifulsoup4>=4.11.0',
      'feedparser>=6.0.0',
      'python-dotenv>=0.19.0',
+     'google-generativeai>=0.3.0',
  ],
```

## 4. 新增文件

### IMPLEMENTATION_SUMMARY.md
- ✅ 已创建
- 包含功能概述、架构特性、实现文件列表、代码质量指标等

### IMPLEMENTATION_CHECKLIST.md
- ✅ 已创建
- 包含完整的实现进度、架构验证、待完成任务等

### RELEASE_v0.1.3_CHECKLIST.md
- ✅ 已创建
- 包含发布前需要更新的所有文档列表

## 5. 支持的搜索引擎更新

在 README.md 中的搜索源表格中，可能需要添加注意：
```markdown
| 源 | API | 特点 | 免费额度 |
|---|---|---|---|
| ... (保持原样) |
| 🤖 **QueryEnhancer** | Google Gemini | LLM 驱动查询优化 | 按 Google 配额 |
```

## 6. 依赖更新

### requirements.txt
```diff
+ google-generativeai>=0.3.0
```

## 📋 文档更新优先级

### 🔴 必须更新（发布前）
1. pyproject.toml - 版本号 + 依赖
2. setup.py - 版本号 + 依赖
3. README.md - 版本号、新特性、更新日志、使用示例

### 🟡 应该更新（发布前最好）
4. CHANGELOG.md / HISTORY.md - 如果存在
5. USAGE_GUIDE.md - 添加查询增强使用说明
6. requirements.txt - 添加新依赖

### 🟢 可以稍后更新
7. 其他文档和示例代码
8. 在线文档（ReadTheDocs）

## 📈 发布时间表

| 步骤 | 时间 | 任务 |
|------|------|------|
| 1 | 前 | 更新所有版本号和依赖 |
| 2 | 前 | 更新 README.md 和使用示例 |
| 3 | 前 | 创建发布分支和 PR |
| 4 | 前 | 最终审查和测试 |
| 5 | 前 | 合并到 master |
| 6 | 发布 | 创建 git tag: v0.1.3 |
| 7 | 发布 | 推送 tag（自动触发 CI/CD） |
| 8 | 后 | 监控 PyPI 发布 |
| 9 | 后 | 创建 GitHub Release 页面 |
| 10 | 后 | 宣传和文档更新 |

## 🔍 验证检查表

发布前需要验证以下内容都已更新：

- [ ] README.md 版本号（第8行）
- [ ] README.md 最新更新部分（第12行）
- [ ] README.md 新特性描述（第13-28行）
- [ ] README.md 使用示例（第120-150行附近）
- [ ] README.md 更新日志（第495行）
- [ ] pyproject.toml 版本号（第7行）
- [ ] pyproject.toml 依赖（第46行）
- [ ] setup.py 版本号（第32行）
- [ ] setup.py 依赖（install_requires）
- [ ] requirements.txt google-generativeai
- [ ] CHANGELOG.md（如果存在）
- [ ] USAGE_GUIDE.md（如果存在）

## 💾 文件大小预期

| 文件 | 预期变化 |
|------|---------|
| README.md | +150-200 行（新示例+更新日志） |
| pyproject.toml | +2-3 行（版本+依赖） |
| setup.py | +2-3 行（版本+依赖） |
| requirements.txt | +1 行（新依赖） |

---

**总结**：
- ✅ 核心代码实现完成（1000+ 行）
- ✅ 测试覆盖完成（8 个测试通过）
- ⏳ 文档更新待执行（预计 20 分钟）
- ⏳ 发布流程待执行（预计 10 分钟）
