# v0.1.3 发布 - 快速参考指南

## 🎯 发布前需要的关键文件修改

### ⚡ 快速修改清单（5分钟速查）

#### 1. pyproject.toml
```diff
第7行：version = "0.1.3"
第46行附近添加：google-generativeai>=0.3.0
```

#### 2. setup.py  
```diff
第32行：version="0.1.3"
在dependencies中添加：'google-generativeai>=0.3.0'
```

#### 3. requirements.txt
```diff
末尾添加：google-generativeai>=0.3.0
```

#### 4. README.md (主要更新)
```diff
第8行：v0.1.2 → v0.1.3
第12行：v0.1.2 → v0.1.3
第13-28行：安全改进 → LLM查询增强
第495行：添加v0.1.3发布日志
在使用示例部分添加新的查询增强示例
```

## 📚 参考文档

已为你创建的发布文档（放在项目根目录）：

1. **RELEASE_v0.1.3_CHECKLIST.md** - 详细的发布前检查清单
2. **DOCUMENTATION_UPDATE_GUIDE.md** - 文档更新对比指南  
3. **IMPLEMENTATION_SUMMARY.md** - 实现功能总结
4. **IMPLEMENTATION_CHECKLIST.md** - 完成情况检查表

## 🔧 发布流程（3步）

### 第1步：更新文档（20分钟）
```bash
# 参考 RELEASE_v0.1.3_CHECKLIST.md 中的具体行号和内容
# 更新以下文件：
1. pyproject.toml
2. setup.py  
3. requirements.txt
4. README.md
```

### 第2步：创建 PR 和发布分支（10分钟）
```bash
# 创建发布分支
git checkout -b release/v0.1.3

# 提交所有更改
git add .
git commit -m "chore: prepare v0.1.3 release - LLM query enhancement"

# 创建 PR
git push origin release/v0.1.3
# 然后在 GitHub 上创建 PR 进行审查
```

### 第3步：合并和发布（5分钟）
```bash
# 合并到 master
git checkout master
git pull origin master
git merge --no-ff release/v0.1.3

# 创建版本标签
git tag -a v0.1.3 -m "Release v0.1.3 - LLM query enhancement"

# 推送（自动触发 CI/CD）
git push origin master
git push origin v0.1.3
```

## ✅ 验证检查项

推送标签后，验证以下内容：

- [ ] GitHub Actions 工作流开始运行
- [ ] 所有测试通过 (GitHub Actions 中可见)
- [ ] PyPI 发布完成 (可在 PyPI 上看到 v0.1.3)
- [ ] Release 页面自动创建

## 📊 v0.1.3 主要变更总结

```
新功能：
- AI 驱动的查询优化（Google Gemini LLM）
- 单一 LLM 调用为所有搜索引擎生成优化查询
- 24 小时智能缓存
- 11 个搜索引擎支持

新文件：
+ ai_news_collector_lib/models/enhanced_query.py (260 行)
+ ai_news_collector_lib/utils/query_enhancer.py (550 行)
+ tests/test_query_enhancer.py (130 行)

新依赖：
+ google-generativeai>=0.3.0

配置新增：
+ enable_query_enhancement
+ llm_provider
+ llm_model
+ llm_api_key
+ query_enhancement_cache_ttl

代码质量：
✅ 8/8 单元测试通过
✅ 20/20 总测试通过  
✅ 81% 代码覆盖率
✅ Flake8 & Black 检查通过
✅ 1000+ 行代码
```

## 🚨 常见陷阱和解决

### 1. 忘记更新版本号
**症状**：PyPI 上没有显示新版本  
**解决**：检查 pyproject.toml 和 setup.py 中的版本号是否都改为 0.1.3

### 2. 忘记添加依赖
**症状**：安装后导入失败 "No module named google.generativeai"  
**解决**：确保在以下 3 个文件中都添加了 google-generativeai>=0.3.0：
- pyproject.toml
- setup.py
- requirements.txt

### 3. 标签推送错误
**症状**：GitHub 上没有看到 Release  
**解决**：确保使用了 `git push origin v0.1.3`（注意是 origin 而不是 upstream）

### 4. CI/CD 失败
**症状**：GitHub Actions 显示红色 ✗  
**解决**：检查工作流日志，通常是因为：
- 依赖安装失败（检查 requirements）
- 测试失败（运行本地 pytest 验证）
- PyPI 凭证问题（通常自动处理）

## 📞 需要帮助？

如果遇到问题，按以下优先级处理：

1. **本地验证**
   ```bash
   pytest -v              # 验证所有测试通过
   flake8 ai_news_collector_lib/
   pip install -e .       # 验证本地安装
   ```

2. **检查文档**
   - 参考 RELEASE_v0.1.3_CHECKLIST.md
   - 参考 DOCUMENTATION_UPDATE_GUIDE.md

3. **检查 GitHub Actions 日志**
   - 在 Actions 标签页查看工作流输出
   - 查找具体的错误信息

4. **回滚方案**（如出现问题）
   ```bash
   # 删除错误的标签
   git tag -d v0.1.3
   git push origin :refs/tags/v0.1.3
   # 修复问题后重新发布
   ```

## 🎉 发布成功标志

当你看到以下信息时，说明发布成功：

✅ GitHub Actions 所有工作流通过  
✅ PyPI 上可以看到 v0.1.3 版本  
✅ 可以用 `pip install ai-news-collector-lib==0.1.3` 安装  
✅ GitHub Release 页面已创建  
✅ 新版本在 https://pypi.org/project/ai-news-collector-lib/ 上可见

## 🚀 发布后建议

1. **更新组织网站/文档**
   - 如有官方文档网站，更新到最新版本

2. **宣传新版本**
   - 在 GitHub Discussion 中宣布
   - 如有社交媒体账号可分享

3. **监控用户反馈**
   - 关注 GitHub Issues
   - 准备好处理bug报告

4. **归档 OpenSpec**
   ```bash
   openspec archive add-query-enhancement-llm --yes
   ```

---

**预计总时间**：~35 分钟  
**发布难度**：⭐⭐☆☆☆ (简单)  
**风险等级**：🟢 低（完全向后兼容）

祝发布顺利！🎉
