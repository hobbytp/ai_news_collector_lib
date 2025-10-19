# GitHub Packages 管理指南

## 📦 关于 GitHub Packages

GitHub Packages 是 GitHub 提供的包托管服务，支持多种包格式。

## 🤔 是否需要发布到 GitHub Packages？

### 对于 Python 包（如本项目）

**推荐：只发布到 PyPI** ✅

**原因**：
1. **用户体验更好**：用户习惯使用 `pip install package-name`
2. **标准做法**：Python 社区的标准是使用 PyPI
3. **无需额外配置**：用户不需要配置额外的包索引
4. **更好的可见性**：PyPI 有更好的搜索和发现机制
5. **维护简单**：只需维护一个包仓库

### GitHub Packages 适用场景

GitHub Packages 更适合以下场景：

1. **私有包**：企业内部包，不想公开到 PyPI
2. **预发布版本**：测试版本，不想污染 PyPI
3. **Docker 镜像**：容器化应用
4. **npm/Maven/NuGet**：其他语言的包

## 📋 当前状态

- ✅ **PyPI**: 已发布 v0.1.0, v0.1.1（即将发布 v0.1.2）
- ⭕ **GitHub Packages**: 未发布（不需要）
- ✅ **GitHub Releases**: 即将设置（用于展示版本历史）

## 🎯 推荐方案

### 方案 1: 保持现状（推荐）⭐

**继续只发布到 PyPI**

这是最常见和推荐的做法，99% 的开源 Python 项目都这样做。

**GitHub Packages 显示 "No packages published" 是正常的**，不影响项目质量。

### 方案 2: 发布 Docker 镜像（可选）

如果你想让 GitHub Packages 有内容显示，可以考虑提供 Docker 镜像：

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "-c", "from ai_news_collector_lib import AINewsCollector; print('Ready!')"]
```

发布 Docker 镜像到 GitHub Container Registry 后，GitHub Packages 会显示容器包。

但这主要是为了展示，对于纯 Python 库不是必需的。

### 方案 3: 镜像发布（不推荐）

同时发布到 PyPI 和 GitHub Packages，但这会：
- 增加维护复杂度
- 用户可能混淆
- 占用 GitHub 存储配额
- 没有实际好处

## 💡 其他展示项目的方式

如果你想让 GitHub 项目页面更丰富，可以：

### 1. 添加徽章（Badges）

在 README.md 中添加：

```markdown
[![PyPI version](https://badge.fury.io/py/ai-news-collector-lib.svg)](https://pypi.org/project/ai-news-collector-lib/)
[![Python Version](https://img.shields.io/pypi/pyversions/ai-news-collector-lib.svg)](https://pypi.org/project/ai-news-collector-lib/)
[![Downloads](https://pepy.tech/badge/ai-news-collector-lib)](https://pepy.tech/project/ai-news-collector-lib)
[![GitHub stars](https://img.shields.io/github/stars/hobbytp/ai_news_collector_lib.svg)](https://github.com/hobbytp/ai_news_collector_lib/stargazers)
[![License](https://img.shields.io/pypi/l/ai-news-collector-lib.svg)](https://github.com/hobbytp/ai_news_collector_lib/blob/master/LICENSE)
```

### 2. 使用 GitHub Releases

✅ 已设置！你的 Release 工作流会自动创建版本发布。

### 3. 完善项目描述

在 GitHub 项目页面：
- Settings → General → Description
- 添加项目描述和标签（topics）
- 添加网站链接（指向 PyPI 或文档）

### 4. 添加 GitHub Actions 徽章

```markdown
[![Tests](https://github.com/hobbytp/ai_news_collector_lib/workflows/Test/badge.svg)](https://github.com/hobbytp/ai_news_collector_lib/actions)
[![Release](https://github.com/hobbytp/ai_news_collector_lib/workflows/Publish/badge.svg)](https://github.com/hobbytp/ai_news_collector_lib/actions)
```

## 📊 对比表

| 特性 | PyPI | GitHub Packages |
|------|------|-----------------|
| Python 社区标准 | ✅ | ❌ |
| 用户体验 | 优秀 | 需要额外配置 |
| 搜索和发现 | 优秀 | 一般 |
| 私有包支持 | 付费 | 免费（有限额） |
| 成本 | 免费（公开包） | 免费（有限额） |
| 适用场景 | 公开包 | 私有包、企业内部 |

## 🎯 结论

**对于 ai-news-collector-lib 项目**：

1. ✅ **继续使用 PyPI 发布公开版本**
2. ✅ **使用 GitHub Releases 展示版本历史**
3. ⭕ **GitHub Packages 保持 "No packages published" 状态（正常）**
4. 🎁 **可选：添加徽章美化 README**

这是最简单、最标准、最受欢迎的方式。

## 🔗 参考链接

- [PyPI 项目页面](https://pypi.org/project/ai-news-collector-lib/)
- [GitHub Packages 文档](https://docs.github.com/en/packages)
- [Python 包发布最佳实践](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
