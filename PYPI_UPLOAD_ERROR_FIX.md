# PyPI 上传问题 - 修复方案

## 问题
```
HTTPError: 400 Bad Request
File already exists ('ai_news_collector_lib-0.1.3-py3-none-any.whl', 
with blake2_256 hash '720403adb456e438c59ed01e4f546121ce9c538a85f7b885eec37293501affe1').
```

PyPI 不允许重新上传相同文件名和版本号的包。

## 根本原因
第一次发布标签 v0.1.3 时虽然工作流失败了，但包已经被上传到 PyPI。现在重新上传相同的包会被拒绝。

## 解决方案

### 方案 1: 清理并重新发布（推荐 - 需要 PyPI 管理员权限）

**步骤：**
1. 登录 PyPI Web 界面
2. 进入项目设置
3. 删除 v0.1.3 的所有文件
4. 等待 5 分钟缓存刷新
5. 重新上传

**命令（本地验证）：**
```bash
twine upload dist/* --skip-existing
```

### 方案 2: 创建补丁版本（快速方案 - 无需管理员）

将版本从 v0.1.3 改为 v0.1.3.post1（表示后发布版本）

**步骤：**
1. 修改 pyproject.toml: version = "0.1.3.post1"
2. 修改 setup.py: version="0.1.3.post1"
3. 创建新标签: v0.1.3.post1
4. 推送标签触发工作流

**优点：**
- 无需管理员权限
- 自动化流程
- PyPI 允许 post 版本号

**缺点：**
- 版本号不够优雅

### 方案 3: 使用 twine 直接上传修复

```bash
# 重新构建包（确保新的包）
python -m build

# 删除旧包
rm dist/ai_news_collector_lib-0.1.3-py3-none-any.whl

# 使用 --skip-existing 标志
twine upload dist/* --skip-existing
```

## 推荐方案

**使用方案 1：清理 PyPI 上的 v0.1.3 后重新上传**

这样最干净，用户看到的就是最终的生产版本。

**操作流程：**
1. 登录 PyPI: https://pypi.org/account/login/
2. 进入项目: https://pypi.org/project/ai-news-collector-lib/
3. 点击 "Project settings" 或 "Manage project"
4. 找到 "Files" 或 "Release history"
5. 删除 v0.1.3 的所有文件
6. 稍等并手动触发工作流或推送新标签

## 临时方案

如果无法访问 PyPI 管理界面，使用方案 2：

```bash
# 更新版本号到 0.1.3.post1
# 提交、标记、推送
# 工作流会自动上传新版本
```

建议：先尝试方案 1（清理并重新发布）。如果需要快速方案，使用 0.1.3.post1。
