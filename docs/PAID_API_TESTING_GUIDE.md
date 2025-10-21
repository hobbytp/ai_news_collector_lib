# 付费API测试指南

## 概述

`test_paid_apis.py` 提供了对所有付费API工具的完整测试覆盖。这个测试设计的核心理念是：
- **首次运行消耗少量API配额**（每个API约1-3个请求）
- **录制HTTP请求到cassette文件**
- **后续可以无限次离线回放**，零成本

---

## 🚀 快速开始

### 第一步：配置 .env 文件

在项目根目录的 `.env` 文件中添加以下配置：

```bash
# 基础配置
ALLOW_NETWORK=1           # 允许网络请求
TEST_PAID_APIS=1         # 启用付费API测试

# 可选：强制重新录制（覆盖现有cassette）
# UPDATE_CASSETTES=1

# 付费API密钥（根据你拥有的API配置）
TAVILY_API_KEY=your_tavily_key_here
GOOGLE_API_KEY=your_google_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
SERPER_API_KEY=your_serper_key_here
BRAVE_API_KEY=your_brave_key_here
METASOTA_API_KEY=your_metasota_key_here
NEWSAPI_KEY=your_newsapi_key_here
```

### 第二步：首次运行（录制请求）

```bash
# 测试所有付费API
python -m pytest tests/test_paid_apis.py -v

# 或者只测试特定API
python -m pytest tests/test_paid_apis.py::test_tavily_search -v
python -m pytest tests/test_paid_apis.py::test_google_search -v
```

**首次运行会：**
- ✅ 执行真实API请求
- ✅ 录制请求/响应到 `tests/cassettes/*.yaml`
- ✅ 验证API返回的数据格式
- 💰 消耗少量API配额（每个API 1-3个请求）

### 第三步：后续运行（离线回放）

录制完成后，可以**移除或注释掉** `.env` 中的配置：

```bash
# ALLOW_NETWORK=1        # 可以关闭
# TEST_PAID_APIS=1       # 可以关闭
# API密钥也可以移除
```

然后继续运行测试，**完全不消耗API配额**：

```bash
python -m pytest tests/test_paid_apis.py -v

# 所有测试将使用录制的cassette运行
```

---

## 📊 测试覆盖范围

### 单元测试（6个）

每个付费API工具都有独立测试：

| 测试函数 | API工具 | Cassette文件 |
|---------|---------|-------------|
| `test_tavily_search` | TavilyTool | `tavily_search.yaml` |
| `test_google_search` | GoogleSearchTool | `google_search.yaml` |
| `test_serper_search` | SerperTool | `serper_search.yaml` |
| `test_brave_search` | BraveSearchTool | `brave_search.yaml` |
| `test_metasota_search` | MetaSotaSearchTool | `metasota_search.yaml` |
| `test_newsapi_search` | NewsAPITool | `newsapi_search.yaml` |

### 集成测试（1个）

`test_paid_apis_integration` - 测试多个付费API同时工作

---

## 🎯 智能跳过机制

测试会自动处理以下情况：

### 情况1：有API密钥 + 无cassette
```
→ 执行真实API请求
→ 录制到cassette
→ 测试通过
```

### 情况2：无API密钥 + 有cassette
```
→ 使用cassette回放
→ 不消耗API配额
→ 测试通过
```

### 情况3：无API密钥 + 无cassette
```
→ 跳过测试（pytest.skip）
→ 显示: "TAVILY_API_KEY 未配置且无cassette"
```

### 情况4：部分API已配置
```
→ 仅测试已配置的API
→ 其他自动跳过
```

---

## 📁 Cassette文件管理

### 录制的文件位置
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

### Cassette内容

每个cassette文件包含：
- ✅ HTTP请求（URL、headers、参数）
- ✅ HTTP响应（状态码、body、headers）
- ✅ 敏感信息已过滤（API密钥、Authorization header）

### 重新录制cassette

如果API响应格式变化，需要重新录制：

```bash
# 方法1：删除旧cassette
rm tests/cassettes/tavily_search.yaml

# 方法2：使用 UPDATE_CASSETTES 强制重录所有
echo "UPDATE_CASSETTES=1" >> .env
python -m pytest tests/test_paid_apis.py -v
```

---

## 💰 成本估算

### 首次录制成本

| API | 请求数 | 预估成本 | 说明 |
|-----|-------|---------|------|
| Tavily | 1请求 | ~$0.001 | 大部分有免费配额 |
| Google Custom Search | 1请求 | $0 | 100次/天免费 |
| Serper | 1请求 | ~$0.001 | 2500次/月免费 |
| Brave Search | 1请求 | ~$0.001 | 2000次/月免费 |
| MetaSota | 1请求 | 取决于定价 | - |
| NewsAPI | 1请求 | $0 | 100次/天免费 |
| **总计** | **7请求** | **<$0.01** | 几乎为零 |

### 后续运行成本

✅ **完全免费** - 使用录制的cassette，零API调用

---

## 🧪 运行示例

### 示例1：测试单个API

```bash
# 设置环境变量
export ALLOW_NETWORK=1
export TEST_PAID_APIS=1
export TAVILY_API_KEY=tvly-xxxxx

# 运行测试
python -m pytest tests/test_paid_apis.py::test_tavily_search -v

# 输出示例：
# tests/test_paid_apis.py::test_tavily_search PASSED [100%]
# 
# ==================== 1 passed in 2.34s ====================
```

### 示例2：测试所有已配置的API

```bash
# 配置多个API密钥在 .env
python -m pytest tests/test_paid_apis.py -v

# 输出示例：
# tests/test_paid_apis.py::test_tavily_search PASSED [ 14%]
# tests/test_paid_apis.py::test_google_search PASSED [ 28%]
# tests/test_paid_apis.py::test_serper_search SKIPPED [ 42%]  # 未配置
# tests/test_paid_apis.py::test_brave_search PASSED [ 57%]
# tests/test_paid_apis.py::test_metasota_search SKIPPED [ 71%]  # 未配置
# tests/test_paid_apis.py::test_newsapi_search PASSED [ 85%]
# tests/test_paid_apis.py::test_paid_apis_integration PASSED [100%]
# 
# ==================== 5 passed, 2 skipped in 8.45s ====================
```

### 示例3：使用cassette离线运行

```bash
# 移除所有API密钥和网络配置
# 直接运行测试
python -m pytest tests/test_paid_apis.py -v

# 所有测试使用cassette，秒速完成
# ==================== 7 passed in 0.15s ====================
```

---

## 📈 提升测试覆盖率

### 运行前的覆盖率
```
tools/search_tools.py: 37% (342行，217行未覆盖)
整体覆盖率: 34%
```

### 运行后的预期覆盖率

```bash
# 运行付费API测试 + 覆盖率分析
python -m pytest tests/test_paid_apis.py \
  --cov=ai_news_collector_lib.tools.search_tools \
  --cov-report=term-missing -v
```

**预期提升：**
- `tools/search_tools.py`: **37% → 65-75%** (+28-38%)
- 整体覆盖率: **34% → 42-45%** (+8-11%)

**覆盖的代码：**
- ✅ TavilyTool 的 search() 方法
- ✅ GoogleSearchTool 的 search() 方法
- ✅ SerperTool 的 search() 方法
- ✅ BraveSearchTool 的 search() 方法
- ✅ MetaSotaSearchTool 的 search() 方法
- ✅ NewsAPITool 的 search() 方法
- ✅ 所有工具的错误处理逻辑
- ✅ API响应解析逻辑
- ✅ 日期过滤逻辑

---

## 🔧 高级配置

### pytest.ini 配置

添加paid_api标记：

```ini
[pytest]
markers =
    network: 标记需要网络的测试
    paid_api: 标记使用付费API的测试
```

### 选择性运行

```bash
# 只运行付费API测试
python -m pytest -m paid_api -v

# 排除付费API测试
python -m pytest -m "not paid_api" -v

# 运行付费API测试 + 生成覆盖率报告
python -m pytest -m paid_api \
  --cov=ai_news_collector_lib \
  --cov-report=html \
  -v
```

---

## 🐛 故障排查

### 问题1：测试被跳过

```
SKIPPED: 付费API测试未启用
```

**解决方案：**
```bash
# 方法1：设置环境变量
export TEST_PAID_APIS=1

# 方法2：提供API密钥
export TAVILY_API_KEY=your_key

# 方法3：使用现有cassette（不需要任何配置）
# 直接运行即可
```

### 问题2：API请求失败

```
AssertionError: 没有任何付费API源成功
```

**解决方案：**
1. 检查API密钥是否正确
2. 检查API配额是否用尽
3. 检查网络连接
4. 删除cassette重新录制

### 问题3：Cassette不匹配

```
CannotOverwriteExistingCassetteException
```

**解决方案：**
```bash
# 删除旧cassette
rm tests/cassettes/*.yaml

# 重新录制
python -m pytest tests/test_paid_apis.py -v
```

---

## 📚 最佳实践

### ✅ 推荐做法

1. **首次录制时使用最小请求数**
   - `max_articles=3` 足够测试
   - `days_back=7` 获取合理的测试数据

2. **提交cassette到Git**
   ```bash
   git add tests/cassettes/*.yaml
   git commit -m "Add paid API test cassettes"
   ```
   - 团队成员可直接使用
   - CI/CD可离线运行

3. **定期更新cassette**
   - API响应格式变化时
   - 重大版本升级前
   - 约3-6个月更新一次

4. **使用不同的查询词**
   - 避免缓存影响
   - 每个API用不同关键词

### ❌ 避免的做法

1. ❌ 在CI中开启 `ALLOW_NETWORK=1`
2. ❌ 使用高频率、大量请求录制
3. ❌ 不提交cassette到版本控制
4. ❌ 在cassette中暴露真实API密钥

---

## 🎉 总结

这个测试方案的优势：

✅ **成本友好** - 首次<$0.01，后续免费  
✅ **覆盖率高** - 预计提升8-11%整体覆盖率  
✅ **灵活可控** - 环境变量精确控制  
✅ **团队友好** - cassette可共享  
✅ **CI/CD友好** - 完全离线运行  
✅ **零维护成本** - 录制一次，用N次  

---

**准备好提升测试覆盖率了吗？**🚀

```bash
# 一键开始
echo "ALLOW_NETWORK=1" >> .env
echo "TEST_PAID_APIS=1" >> .env
python -m pytest tests/test_paid_apis.py -v --cov=ai_news_collector_lib
```
