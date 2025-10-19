# Release 流程指南

本文档说明如何发布新版本到 PyPI 和 GitHub。

## 版本号规范

遵循 [语义化版本](https://semver.org/lang/zh-CN/) (SemVer) 规范：

- **主版本号 (MAJOR)**：不兼容的 API 修改
- **次版本号 (MINOR)**：向下兼容的功能性新增
- **修订号 (PATCH)**：向下兼容的问题修正

示例：`v0.1.1` → 主版本=0，次版本=1，修订号=1

## 发布前检查清单

- [ ] 所有测试通过 (`python -m pytest -v`)
- [ ] 代码已合并到 `master` 分支
- [ ] 版本号已更新在以下文件：
  - `ai_news_collector_lib/__init__.py`
  - `setup.py`
  - `pyproject.toml`
- [ ] `CHANGELOG.md` 已更新（如果有）
- [ ] 文档已更新（README.md, USAGE_GUIDE.md 等）

## 发布步骤

### 1. 更新版本号

在三个文件中更新版本号为新版本（如 `0.1.3`）：

```python
# ai_news_collector_lib/__init__.py
__version__ = "0.1.3"

# setup.py
setup(
    name="ai-news-collector-lib",
    version="0.1.3",
    # ...
)

# pyproject.toml
[project]
name = "ai-news-collector-lib"
version = "0.1.3"
```

### 2. 提交版本更新

```bash
git add ai_news_collector_lib/__init__.py setup.py pyproject.toml
git commit -m "chore(release): bump version to 0.1.3"
git push origin master
```

### 3. 创建并推送 Git Tag

```bash
# 创建带注释的 tag
git tag -a v0.1.3 -m "Release v0.1.3

- 新功能1
- Bug修复1
- 文档更新
"

# 推送 tag 到 GitHub
git push origin v0.1.3
```

### 4. 自动创建 GitHub Release

推送 tag 后，GitHub Actions 会自动：
- 创建 GitHub Release
- 生成 Release Notes
- 关联到 PyPI 包

查看进度：https://github.com/hobbytp/ai_news_collector_lib/actions

### 5. 发布到 PyPI

```bash
# 确保环境变量已设置（在 .env 文件中）
# PYPI_API_TOKEN=pypi-xxxxx

# 运行上传脚本
python upload_to_pypi.py
```

脚本会自动：
- 清理旧的构建文件
- 使用 build 构建包
- 使用 twine 上传到 PyPI
- 显示上传结果

### 6. 验证发布

1. **验证 PyPI**：
   ```bash
   pip install ai-news-collector-lib==0.1.2
   python -c "import ai_news_collector_lib; print(ai_news_collector_lib.__version__)"
   ```

2. **验证 GitHub Release**：
   访问 https://github.com/hobbytp/ai_news_collector_lib/releases

3. **验证文档**：
   确保 PyPI 页面显示正确的 README

## 补充历史 Release

如果需要为历史版本创建 Release：

```bash
# 找到对应的 commit hash
git log --oneline

# 为特定 commit 创建 tag
git tag -a v0.1.0 <commit-hash> -m "Release v0.1.0"

# 推送 tag
git push origin v0.1.0
```

GitHub Actions 会自动创建对应的 Release。

## 回滚 Release

如果需要撤销错误的 release：

```bash
# 删除本地 tag
git tag -d v0.1.2

# 删除远程 tag
git push origin :refs/tags/v0.1.2

# 在 GitHub 上手动删除 Release
# Settings → Releases → 找到对应版本 → Delete
```

## 常见问题

### Q: Tag 推送了但没有创建 Release？

检查：
1. GitHub Actions 是否运行成功
2. Tag 名称是否符合 `v*.*.*` 格式
3. 仓库权限设置是否正确

### Q: PyPI 和 GitHub 版本不一致？

确保：

1. 先更新代码中的版本号
2. 提交并推送到 master
3. 创建对应的 git tag
4. 再运行 upload_to_pypi.py

### Q: 如何发布预发布版本？

使用预发布版本号，如：

- `v0.2.0-alpha.1`
- `v0.2.0-beta.1`
- `v0.2.0-rc.1`

在 PyPI 上传时会自动标记为预发布版本。

## 版本历史

- **v0.1.0** (2025-10-15): 初始发布，基础功能
- **v0.1.1** (2025-10-17): Bug 修复（ArXiv、MetaSota）
- **v0.1.2** (2025-10-19): 测试基础设施改进（PR #2）

## 相关链接

- [PyPI 项目页面](https://pypi.org/project/ai-news-collector-lib/)
- [GitHub Releases](https://github.com/hobbytp/ai_news_collector_lib/releases)
- [GitHub Actions](https://github.com/hobbytp/ai_news_collector_lib/actions)
- [语义化版本规范](https://semver.org/lang/zh-CN/)
