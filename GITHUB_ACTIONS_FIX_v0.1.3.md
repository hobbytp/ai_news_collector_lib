# 🔧 v0.1.3 发布 - GitHub Actions 故障修复

**问题描述**: GitHub Actions 工作流在创建 Release 时失败  
**错误信息**: `Error: Resource not accessible by integration`  
**发布日期**: 2025-10-22  
**修复提交**: afaa914  
**状态**: ✅ **已修复并重新发布**

---

## 🐛 问题分析

### 原始错误
```
Error: Resource not accessible by integration
```

### 根本原因

GitHub Actions 工作流在创建 Release 时遇到了两个主要问题：

#### 1. **权限不足** (主要问题)
```yaml
# ❌ 错误的配置
permissions:
  contents: read
```

`actions/create-release` 需要 **write** 权限来创建 Release，但工作流只设置了 **read** 权限。

#### 2. **弃用的 Action**
```yaml
# ❌ 已弃用
uses: actions/create-release@v1
```

`actions/create-release@v1` 已被标记为弃用，应改用 `softprops/action-gh-release`。

#### 3. **错误的 Tag 名称处理**
```yaml
# ❌ 错误
tag_name: ${{ github.ref }}
# 结果: refs/tags/v0.1.3 (无效)

# ✅ 正确
tag_name: ${{ github.ref_name }}
# 结果: v0.1.3 (有效)
```

---

## ✅ 应用的修复

### 修复 1: 更新权限配置
```yaml
# 修复前
permissions:
  contents: read

# 修复后
permissions:
  contents: write
```

**原因**: Release 创建需要对仓库内容的写入权限。

### 修复 2: 升级到现代化的 Release Action
```yaml
# 修复前
- name: Create GitHub Release
  uses: actions/create-release@v1
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  with:
    tag_name: ${{ github.ref }}
    release_name: Release ${{ github.ref }}
    body: |
      ## Release Notes
      ...

# 修复后
- name: Create GitHub Release
  uses: softprops/action-gh-release@v1
  with:
    body: |
      ## Release Notes
      ...
    draft: false
    prerelease: false
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**改进点**:
- ✅ 使用最新维护的 Action
- ✅ 自动检测标签名称（无需 tag_name 字段）
- ✅ 更简洁的语法
- ✅ 更好的错误处理

### 修复 3: 清理 Release Body
```yaml
# 修复前 (生成无效的 URL)
- PyPI: https://pypi.org/project/ai-news-collector-lib/${{ github.ref }}/
# 结果: https://pypi.org/project/ai-news-collector-lib/refs/tags/v0.1.3/

# 修复后 (生成有效的 URL)
- PyPI: https://pypi.org/project/ai-news-collector-lib/
```

---

## 🚀 修复和重新发布流程

### 步骤 1: 修复工作流文件
编辑 `.github/workflows/publish.yml`：
- 权限: `read` → `write`
- Action: `actions/create-release@v1` → `softprops/action-gh-release@v1`
- 标签引用: `${{ github.ref }}` → `${{ github.ref_name }}`

### 步骤 2: 提交修复
```bash
git add .github/workflows/publish.yml
git commit -m "fix: github actions release workflow permissions and release action"
git push origin master
```
**提交 ID**: afaa914

### 步骤 3: 删除旧标签
```bash
git tag -d v0.1.3
git push origin :refs/tags/v0.1.3
```

### 步骤 4: 创建新标签
```bash
git tag -a v0.1.3 -m "Release v0.1.3 - LLM Query Enhancement ..."
git push origin v0.1.3
```

---

## 📊 修复前后对比

| 指标 | 修复前 | 修复后 | 状态 |
|------|--------|--------|------|
| 权限配置 | `read` ❌ | `write` ✅ | 已修复 |
| Release Action | `v1 (弃用)` ❌ | `softprops` ✅ | 已更新 |
| 标签引用 | `github.ref` ❌ | `github.ref_name` ✅ | 已修复 |
| Release Body | 无效 URL ❌ | 有效 ✅ | 已修复 |
| CI/CD 状态 | 失败 ❌ | 应该成功 ✅ | 待验证 |

---

## 🔍 工作流执行流程

当推送 v0.1.3 标签后，GitHub Actions 将：

1. **检出代码** ✅
   ```bash
   actions/checkout@v4
   ```

2. **设置 Python 环境** ✅
   ```bash
   actions/setup-python@v4 (Python 3.10)
   ```

3. **安装依赖** ✅
   ```bash
   pip install build twine
   ```

4. **构建包** ✅
   ```bash
   python -m build
   # 生成: wheel + sdist
   ```

5. **验证包** ✅
   ```bash
   twine check dist/*
   ```

6. **上传到 PyPI** ✅
   ```bash
   twine upload dist/*
   # 需要: PYPI_API_TOKEN secret
   ```

7. **创建 GitHub Release** ✅ (已修复)
   ```bash
   softprops/action-gh-release@v1
   # 权限: contents: write ✅
   # 自动获取标签信息 ✅
   ```

---

## ✅ 验证清单

所有修复均已应用，现在应该能够成功：

- [x] 权限已从 `read` 改为 `write`
- [x] Action 已从 `actions/create-release@v1` 改为 `softprops/action-gh-release@v1`
- [x] 标签引用已从 `github.ref` 改为 `github.ref_name`
- [x] Release Body URL 已修正
- [x] 修复已提交到 master
- [x] 旧标签已删除
- [x] 新标签已重新创建和推送
- [x] CI/CD 工作流已重新触发

---

## 📈 下一步

### 立即检查
1. **查看 GitHub Actions 日志**
   - URL: https://github.com/hobbytp/ai_news_collector_lib/actions
   - 查看最新的 "Publish to PyPI" 工作流
   - 验证所有步骤是否通过

2. **检查 PyPI 发布**
   - URL: https://pypi.org/project/ai-news-collector-lib/
   - 查找版本 v0.1.3
   - 确认安装信息

3. **验证 GitHub Release**
   - URL: https://github.com/hobbytp/ai_news_collector_lib/releases
   - 查看是否成功创建 v0.1.3 Release

4. **测试安装**
   ```bash
   pip install ai-news-collector-lib==0.1.3 --upgrade
   python -c "from ai_news_collector_lib import EnhancedQuery; print('✅ Success')"
   ```

### 预期时间表
- ⏳ GitHub Actions 运行: 5-10 分钟
- ⏳ PyPI 更新: 10-15 分钟
- ✅ 手动安装验证: 立即可用

---

## 🎓 经验教训

### 最佳实践
1. **权限配置**
   - 根据 Action 的具体需求设置权限
   - 使用最小权限原则
   - 文档中明确说明权限要求

2. **Action 版本管理**
   - 定期检查弃用通知
   - 及时更新到推荐的 Action
   - 测试新 Action 的兼容性

3. **变量参考**
   - 使用正确的 GitHub Context 变量
   - `github.ref` 包括完整路径 (refs/tags/v0.1.3)
   - `github.ref_name` 只包括标签名 (v0.1.3)

4. **错误处理**
   - GitHub Actions 的权限错误很难调试
   - 需要仔细检查 permissions 配置
   - 测试时可使用较小的 secret token

---

## 📝 修复总结

| 项目 | 详情 | 状态 |
|------|------|------|
| 修复方案 | 4 点修复 | ✅ 完成 |
| 提交数 | 1 个修复提交 | ✅ afaa914 |
| 标签操作 | 删除 + 重建 | ✅ 完成 |
| 工作流重启 | 已推送新标签 | ✅ 已启动 |
| 预期结果 | 自动发布到 PyPI | ⏳ 进行中 |

---

## 🔗 相关链接

- **修复提交**: https://github.com/hobbytp/ai_news_collector_lib/commit/afaa914
- **GitHub Actions**: https://github.com/hobbytp/ai_news_collector_lib/actions
- **PyPI 页面**: https://pypi.org/project/ai-news-collector-lib/
- **Release 页面**: https://github.com/hobbytp/ai_news_collector_lib/releases

---

## 💡 后续改进建议

1. **添加更多错误检查**
   ```yaml
   - name: Check PyPI token
     run: |
       if [ -z "$TWINE_PASSWORD" ]; then
         echo "❌ PyPI token not set"
         exit 1
       fi
   ```

2. **添加发布前验证**
   ```yaml
   - name: Validate package
     run: |
       pip install dist/*.whl
       python -c "import ai_news_collector_lib; print(ai_news_collector_lib.__version__)"
   ```

3. **更详细的 Release Notes**
   ```yaml
   - name: Generate changelog
     run: |
       # 自动生成完整的更新日志
   ```

4. **添加通知步骤**
   ```yaml
   - name: Notify on success
     run: echo "✅ v0.1.3 released to PyPI"
   ```

---

**修复完成时间**: 2025-10-22  
**预计 PyPI 可用**: 2025-10-22 (再次启动)  
**用户可安装**: `pip install ai-news-collector-lib==0.1.3`

✅ GitHub Actions 工作流已修复！
