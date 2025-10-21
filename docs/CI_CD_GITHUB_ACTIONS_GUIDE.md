# pytest 和 .env 加载 + GitHub Actions 集成指南

## 1️⃣ 问题解答

### Q1: `python -m pytest tests/test_paid_apis.py -v` 会自动加载 .env 吗？

**答：✅ 会的！**

```python
# tests/conftest.py 中已配置
from dotenv import load_dotenv

load_dotenv()  # 自动在pytest启动时加载
```

**为什么自动加载？**
- conftest.py 是pytest的特殊文件，在运行任何测试前会被加载
- `load_dotenv()` 会自动查找项目根目录的 `.env` 文件
- 加载的变量通过 `os.getenv()` 访问

**验证方式：**
```bash
# 直接运行，无需 source .env
python -m pytest tests/test_paid_apis.py -v

# .env 中的变量会自动可用
# TEST_PAID_APIS=1 已生效
```

---

### Q2: 需要用户手动 `source .env` 吗？

**答：❌ 不需要！**

当前设计：
```python
# ✅ 推荐方式：自动加载
python -m pytest tests/test_paid_apis.py -v  # .env 自动加载

# ❌ 不推荐：需要手动加载
source .env
python -m pytest tests/test_paid_apis.py -v  # 多余的一步
```

**为什么？**
- Python dotenv包在conftest.py中已自动加载
- 跨平台兼容（Windows批处理/Linux shell都支持）
- 开发者体验更好

---

### Q3: 能集成到GitHub Actions CI吗？

**答：✅ 可以！** 

我会提供3个集成方案：
1. **基础方案** - 使用cassettes离线运行
2. **高级方案** - 设置付费API密钥后自动录制
3. **混合方案** - 本地录制，CI离线运行

---

## 2️⃣ GitHub Actions 集成方案

### 方案1：基础方案（推荐用于v0.1.2发布）

**特点：**
- ✅ 完全离线运行
- ✅ 无需API密钥
- ✅ 速度快（<1秒）
- ✅ 可靠性高

**文件：`.github/workflows/test-paid-apis-offline.yml`**

```yaml
name: Test Paid APIs (Offline with Cassettes)

on:
  push:
    branches: [master, develop]
  pull_request:
    branches: [master, develop]

jobs:
  test-paid-apis:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install pytest pytest-asyncio pyyaml vcrpy
      
      - name: Run paid API tests (offline with cassettes)
        run: python -m pytest tests/test_paid_apis.py -v
      
      - name: Generate coverage report
        run: |
          pip install pytest-cov
          python -m pytest tests/test_paid_apis.py \
            --cov=ai_news_collector_lib.tools.search_tools \
            --cov-report=xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: paid-apis
          name: paid-apis-coverage
```

### 方案2：高级方案（需要API密钥）

**特点：**
- ✅ 首次运行录制cassettes
- ✅ 后续运行使用cassettes
- ✅ 定期更新cassettes
- ⚠️ 需要在GitHub Secrets中配置API密钥

**文件：`.github/workflows/test-paid-apis-record.yml`**

```yaml
name: Record/Update Paid API Cassettes

on:
  schedule:
    # 每月第一天 UTC 00:00 运行
    - cron: '0 0 1 * *'
  workflow_dispatch:  # 手动触发
  
jobs:
  record-cassettes:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install pytest pytest-asyncio pyyaml vcrpy
      
      - name: Create .env file with API keys
        run: |
          cat > .env << EOF
          ALLOW_NETWORK=1
          TEST_PAID_APIS=1
          UPDATE_CASSETTES=1
          
          TAVILY_API_KEY=${{ secrets.TAVILY_API_KEY }}
          GOOGLE_API_KEY=${{ secrets.GOOGLE_API_KEY }}
          GOOGLE_SEARCH_ENGINE_ID=${{ secrets.GOOGLE_SEARCH_ENGINE_ID }}
          SERPER_API_KEY=${{ secrets.SERPER_API_KEY }}
          BRAVE_API_KEY=${{ secrets.BRAVE_API_KEY }}
          METASOTA_API_KEY=${{ secrets.METASOTA_API_KEY }}
          NEWSAPI_KEY=${{ secrets.NEWSAPI_KEY }}
          EOF
      
      - name: Run paid API tests and record cassettes
        run: python -m pytest tests/test_paid_apis.py -v
      
      - name: Commit cassette changes
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "chore: update API cassettes"
          file_pattern: tests/cassettes/*.yaml
          skip_fetch: true
          skip_checkout: true
      
      - name: Create Pull Request if cassettes changed
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "chore: update API cassettes"
          title: "chore: Update API cassettes"
          body: "Automated cassette update from GitHub Actions"
          branch: update-cassettes
          delete-branch: true
```

### 方案3：混合方案（本地录制 + CI离线）

**特点：**
- ✅ 开发者本地录制cassettes
- ✅ CI完全离线运行
- ✅ 成本最低
- ✅ 最实用

**文件：`.github/workflows/test.yml`（主测试工作流）**

```yaml
name: Tests

on:
  push:
    branches: [master, develop]
  pull_request:
    branches: [master, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install pytest pytest-asyncio pytest-cov pyyaml vcrpy
      
      - name: Lint with flake8
        run: |
          pip install flake8
          flake8 ai_news_collector_lib/core/ --max-line-length=88
      
      - name: Run all tests (with cassettes for paid APIs)
        run: python -m pytest tests/ -v --cov=ai_news_collector_lib
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

## 3️⃣ 设置GitHub Secrets（可选，用于方案2）

### 步骤1：在GitHub仓库中添加Secrets

路径：**Settings → Secrets and variables → Actions → New repository secret**

添加以下secrets（根据你拥有的API配置）：

```
TAVILY_API_KEY: tvly-xxxxx
GOOGLE_API_KEY: AIzaSy...
GOOGLE_SEARCH_ENGINE_ID: xxxxx
SERPER_API_KEY: xxxxx
BRAVE_API_KEY: xxxxx
METASOTA_API_KEY: xxxxx
NEWSAPI_KEY: xxxxx
```

### 步骤2：验证Secrets

在workflow中使用：
```yaml
env:
  API_KEY: ${{ secrets.TAVILY_API_KEY }}
```

---

## 4️⃣ 自动化流程图

```
开发流程：
┌─────────────────────────────────────────┐
│ 1. 本地开发（无需付费API）              │
│ • 使用免费源（HN, ArXiv, DDG）          │
│ • 所有测试都会通过                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. 准备发布新功能时                     │
│ • 在 .env 配置API密钥                   │
│ • 运行: pytest tests/test_paid_apis.py  │
│ • 自动录制 cassettes                    │
│ • 提交 cassettes 到仓库                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 3. 创建PR时                             │
│ • GitHub Actions 自动运行               │
│ • 使用录制的 cassettes                  │
│ • 完全离线，0 秒内完成                  │
│ • 覆盖率自动上传到 Codecov              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 4. 合并到主分支                         │
│ • CI 再次运行所有测试                   │
│ • 确保没有回归                          │
└─────────────────────────────────────────┘
```

---

## 5️⃣ 具体配置步骤

### 第一步：选择集成方案

根据你的需求选择：

**选项A：基础方案（推荐）**
```bash
mkdir -p .github/workflows
cp .github/workflows/test-paid-apis-offline.yml .github/workflows/
```

**选项B：高级方案**
```bash
# 需要在GitHub添加Secrets
# 然后添加workflow文件
```

**选项C：混合方案（最实用）**
```bash
# 推荐使用这个方案
# 本地录制，CI离线
```

### 第二步：配置cassettes自动提交

如果使用方案2（高级），添加：
```bash
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
```

### 第三步：验证工作流

```bash
# 检查workflow文件语法
act -l  # 需要安装 https://github.com/nektos/act

# 或直接提交到GitHub，查看Actions标签
```

---

## 6️⃣ 最佳实践

### ✅ 推荐做法

1. **使用方案3（混合方案）**
   - 开发者本地处理API录制
   - CI完全离线运行
   - 成本最低，可靠性最高

2. **将cassettes提交到Git**
   ```bash
   git add tests/cassettes/*.yaml
   git commit -m "Add/update API cassettes"
   ```

3. **CI中只运行离线测试**
   ```yaml
   python -m pytest tests/test_paid_apis.py -v
   # cassettes 已在仓库中
   ```

4. **定期更新cassettes**
   ```bash
   # 每个季度手动运行一次
   UPDATE_CASSETTES=1 python -m pytest tests/test_paid_apis.py -v
   ```

### ❌ 避免做法

1. ❌ 在CI中配置所有API密钥
   - 存在安全风险
   - 每次都消耗API配额

2. ❌ 不提交cassettes
   - CI无法运行
   - 开发体验差

3. ❌ 频繁运行录制workflow
   - 浪费API配额
   - 不必要的成本

---

## 7️⃣ 现成的GitHub Actions文件

现在让我为你创建这些文件：

---

## 🎯 即刻可用的解决方案

创建以下文件到你的仓库：

```bash
.github/
├── workflows/
│   ├── test.yml                      # 主测试工作流
│   ├── test-paid-apis.yml            # 付费API测试
│   └── update-cassettes.yml          # 定期更新cassettes（可选）
└── GITHUB_ACTIONS_SETUP.md           # 设置指南
```

---

## 🚀 快速集成步骤

### 1. 复制workflow文件

```bash
# 创建目录
mkdir -p .github/workflows

# 复制文件（我会帮你创建）
cp workflows/*.yml .github/workflows/
```

### 2. 提交到仓库

```bash
git add .github/workflows/
git commit -m "Add GitHub Actions CI/CD workflows"
git push
```

### 3. 验证

在GitHub查看 **Actions** 标签，应该看到工作流自动运行

### 4. 配置Secrets（可选）

如果使用方案2或定期更新cassettes：
- Settings → Secrets → 添加API密钥

---

## 📊 预期结果

### 自动化流程

```
PR提交 → GitHub Actions自动运行 → 检查覆盖率 → 自动上传Codecov
   ↓                              ↓
  付费API测试                   代码质量检查
  (离线, <1秒)                  (flake8/black)
   ↓
通过/失败 → 在PR中显示检查状态
```

### CI中的日志示例

```
✅ Run paid API tests (offline with cassettes)
tests/test_paid_apis.py::test_tavily_search PASSED [ 14%]
tests/test_paid_apis.py::test_google_search PASSED [ 28%]
tests/test_paid_apis.py::test_serper_search PASSED [ 42%]
tests/test_paid_apis.py::test_brave_search PASSED [ 57%]
tests/test_paid_apis.py::test_metasota_search PASSED [ 71%]
tests/test_paid_apis.py::test_newsapi_search PASSED [ 85%]
tests/test_paid_apis.py::test_paid_apis_integration PASSED [100%]

======================== 7 passed in 0.45s ========================

✅ Coverage: 45% (up from 34%)
✅ Codecov uploaded
```

---

## 💡 总结

### 关于 .env 自动加载

✅ **已自动配置**
- conftest.py 中的 `load_dotenv()` 会自动加载
- 无需用户手动 `source .env`

### 关于 GitHub Actions 集成

✅ **支持3种方案**

| 方案 | 难度 | 成本 | 推荐度 | 说明 |
|------|------|------|--------|------|
| 基础（离线） | ⭐ | 免费 | ⭐⭐⭐ | 完全离线，现在就能用 |
| 高级（录制） | ⭐⭐ | <$1/月 | ⭐⭐ | 需要API密钥 |
| 混合 | ⭐⭐ | 免费 | ⭐⭐⭐ | 最平衡的方案 |

现在我会为你创建现成的workflow文件！准备好了吗？ 🚀
