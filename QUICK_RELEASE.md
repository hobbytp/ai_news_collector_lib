# 快速操作：发布 v0.1.5 到 GitHub 和 PyPI

## 📋 版本对应关系（已确认）

- **v0.1.4** → PyPI ✓ | GitHub ✓ (Release v0.1.4)
- **v0.1.5** → PyPI ✗ | GitHub ✗ (当前版本，准备发布)

## 🚀 操作步骤

### 步骤 1: 构建包（已完成）

```bash
# 构建生成 dist/ 目录下的 .whl 和 .tar.gz 文件
uv build
# 或
python -m build
```

### 步骤 2: 为 v0.1.5 创建 tag

```bash
# 确保在 master 分支且已同步最新代码
git checkout master
git pull origin master

# 创建 v0.1.5 tag
git tag -a v0.1.5 -m "Release v0.1.5 - Added YouTube, GitHub, HuggingFace, Perplexity search engines

## 新功能

- 新增 YouTube 搜索支持
- 新增 GitHub 搜索支持
- 新增 HuggingFace 搜索支持
- 新增 Perplexity AI 搜索支持
- 统一时间过滤逻辑 (BaseSearchTool._parse_iso_datetime)
- 增强 HTTP 请求鲁棒性 (自动重试)

## 文档

- 更新 README.md 添加新引擎配置
- 移除过时的 Bing 配置
"

# 推送 tag
git push origin v0.1.5
```

### 步骤 3: 等待 GitHub Release 自动创建

访问 https://github.com/hobbytp/ai_news_collector_lib/actions 查看进度。

### 步骤 4: 发布到 PyPI (手动)

由于上传脚本可能遇到网络问题 (WinError 10061)，请手动执行上传或确保代理配置正确。

**方法 A: 使用脚本（需设置 HTTPS_PROXY）**

```bash
# 设置代理 (PowerShell)
$env:HTTPS_PROXY="http://127.0.0.1:7890"

# 运行上传脚本
python upload_to_pypi.py
```

**方法 B: 手动使用 Twine**

```bash
# 安装 twine
pip install twine

# 上传
twine upload dist/*
```

### 步骤 5: 验证发布

```bash
# 验证 PyPI 安装
pip install --upgrade ai-news-collector-lib==0.1.5
python -c "import ai_news_collector_lib; print(ai_news_collector_lib.__version__)"
# 应该输出: 0.1.5
```

```bash
# 在 Windows Git Bash 或 Linux/Mac 终端执行
bash scripts/create_historical_tags.sh

# 推送历史 tags 到 GitHub
git push origin v0.1.0 v0.1.1
```

这会自动触发 GitHub Actions 为 v0.1.0 和 v0.1.1 创建 Release。

### 步骤 2: 为 v0.1.2 创建 tag

```bash
# 确保在 master 分支且已同步最新代码
git checkout master
git pull origin master

# 创建 v0.1.2 tag
git tag -a v0.1.2 -m "Release v0.1.2 - Testing infrastructure improvements

## 新功能

- 新增离线测试工作流与 VCR 磁带录制/回放
- 完善 CI/CD 测试流程（pytest + GitHub Actions）
- 新增测试文档（TESTING_GUIDE.md）

## Bug 修复

- 修复 DailyScheduler 可选导入问题
- 统一使用时区感知的 datetime
- 改进 PyPI 上传脚本

## 文档

- 新增 RELEASE_GUIDE.md 发布流程指南
- 更新 TESTING_GUIDE.md 测试指南
- 新增 .env.example 环境变量示例

## CI/CD

- 新增 .github/workflows/test.yml
- 更新 .github/workflows/publish.yml
- 新增 .github/workflows/release.yml
"

# 推送 tag
git push origin v0.1.2
```

### 步骤 3: 等待 GitHub Release 自动创建

访问 https://github.com/hobbytp/ai_news_collector_lib/actions 查看进度。

完成后访问 https://github.com/hobbytp/ai_news_collector_lib/releases 确认。

### 步骤 4: 发布到 PyPI

```bash
# 确保 .env 文件中有 PYPI_API_TOKEN
# PYPI_API_TOKEN=pypi-xxxxx

# 运行上传脚本
python upload_to_pypi.py
```

### 步骤 5: 验证发布

```bash
# 验证 PyPI 安装
pip install --upgrade ai-news-collector-lib==0.1.2
python -c "import ai_news_collector_lib; print(ai_news_collector_lib.__version__)"

# 应该输出: 0.1.2
```

## ✅ 完成后检查

- [ ] GitHub 上有 3 个 Release: v0.1.0, v0.1.1, v0.1.2
- [ ] PyPI 上有 3 个版本: 0.1.0, 0.1.1, 0.1.2
- [ ] 版本号匹配且都可以安装
- [ ] Release Notes 自动生成且准确

## 📝 注意事项

1. **历史 tags 只需创建一次**：v0.1.0 和 v0.1.1 的 tags 创建并推送后不需要再操作
2. **未来发布更简单**：只需更新版本号 → 提交 → 创建 tag → 推送
3. **自动化流程**：推送 tag 后 GitHub Release 会自动创建
4. **版本一致性**：确保 GitHub tag 和 PyPI 版本号对应

## 🔗 相关链接

- [完整发布指南](./RELEASE_GUIDE.md)
- [测试指南](./TESTING_GUIDE.md)
- [PyPI 上传指南](./PYPI_RELEASE_GUIDE.md)
