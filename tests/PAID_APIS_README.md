# 付费API测试 - 快速开始 🚀

这个测试方案让你能够：
- ✅ 以最小成本（<$0.01）测试所有付费API
- ✅ 录制HTTP请求后可以**无限次离线回放**
- ✅ 提升测试覆盖率约 **8-11%**
- ✅ 零维护成本，一次录制永久使用

---

## 📝 快速开始（3步）

### 步骤1：配置API密钥

编辑 `.env` 文件，添加你拥有的API密钥：

```bash
# 基础配置
ALLOW_NETWORK=1
TEST_PAID_APIS=1

# 添加你的API密钥（根据你拥有的配置）
TAVILY_API_KEY=tvly-xxxxx
GOOGLE_API_KEY=AIzaSy...
GOOGLE_SEARCH_ENGINE_ID=xxxxx
SERPER_API_KEY=xxxxx
# ... 其他API密钥
```

### 步骤2：首次运行（录制）

**Windows用户：**
```bash
scripts\test_paid_apis.bat
# 选择选项 1
```

**Linux/Mac用户：**
```bash
bash scripts/test_paid_apis.sh
# 选择选项 1
```

**或者直接运行：**
```bash
python -m pytest tests/test_paid_apis.py -v
```

💰 **成本**：约 <$0.01（每个API 1-3个请求）

### 步骤3：后续运行（离线）

录制完成后，可以**移除API密钥**，直接运行：

```bash
python -m pytest tests/test_paid_apis.py -v
```

✅ 完全免费，使用录制的cassette回放

---

## 📊 覆盖率提升

运行付费API测试后：

```bash
python -m pytest tests/test_paid_apis.py \
  --cov=ai_news_collector_lib \
  --cov-report=html -v
```

**预期结果：**
- `tools/search_tools.py`: 37% → **65-75%** (+28-38%)
- 整体覆盖率: 34% → **42-45%** (+8-11%)

---

## 🎯 测试范围

### 6个单元测试
- ✅ TavilyTool
- ✅ GoogleSearchTool
- ✅ SerperTool
- ✅ BraveSearchTool
- ✅ MetaSotaSearchTool
- ✅ NewsAPITool

### 1个集成测试
- ✅ 多个付费API同时工作

---

## 📁 录制的Cassettes

首次运行后会在 `tests/cassettes/` 生成：

```
tests/cassettes/
├── tavily_search.yaml
├── google_search.yaml
├── serper_search.yaml
├── brave_search.yaml
├── metasota_search.yaml
├── newsapi_search.yaml
└── paid_apis_integration.yaml
```

**建议提交到Git**，团队成员可直接使用！

---

## 🔧 高级用法

### 仅测试特定API

```bash
# 只测试Tavily
python -m pytest tests/test_paid_apis.py::test_tavily_search -v

# 只测试Google Search
python -m pytest tests/test_paid_apis.py::test_google_search -v
```

### 强制重新录制

```bash
# 方法1：删除旧cassette
rm tests/cassettes/tavily_search.yaml
python -m pytest tests/test_paid_apis.py::test_tavily_search -v

# 方法2：使用环境变量
UPDATE_CASSETTES=1 python -m pytest tests/test_paid_apis.py -v
```

### 使用pytest标记

```bash
# 只运行付费API测试
python -m pytest -m paid_api -v

# 排除付费API测试
python -m pytest -m "not paid_api" -v
```

---

## 💡 智能跳过逻辑

测试会自动处理各种情况：

| 情况 | 行为 |
|------|------|
| 有API密钥 + 无cassette | ✅ 执行真实请求并录制 |
| 无API密钥 + 有cassette | ✅ 使用cassette回放 |
| 无API密钥 + 无cassette | ⏭️ 跳过测试 |
| 部分API已配置 | ✅ 仅测试已配置的 |

---

## 📖 完整文档

详细说明请查看：
- 📘 [PAID_API_TESTING_GUIDE.md](../PAID_API_TESTING_GUIDE.md) - 完整使用指南
- 📊 [COVERAGE_SUMMARY_v0.1.2.md](../COVERAGE_SUMMARY_v0.1.2.md) - 覆盖率分析

---

## 🎉 总结

这个方案的优势：

✅ **成本友好** - 首次<$0.01，后续完全免费  
✅ **覆盖率高** - 提升8-11%整体覆盖率  
✅ **零维护** - 录制一次，永久使用  
✅ **团队友好** - cassette可共享  
✅ **CI/CD友好** - 完全离线运行  

---

**准备好了吗？开始测试！** 🚀

```bash
# Windows
scripts\test_paid_apis.bat

# Linux/Mac
bash scripts/test_paid_apis.sh
```
