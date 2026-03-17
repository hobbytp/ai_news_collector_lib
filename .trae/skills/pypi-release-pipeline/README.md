# pypi-release-pipeline

面向 Python 库发布的 Agent Skill，按 `agentskills.io` 规范封装发布流程，支持原子步骤执行、超时重试、失败回滚、CI/CD 生命周期管理。

## 快速开始

1. 准备请求文件：

```json
{
  "version": "0.1.6",
  "repo_root": "f:/AI/src/ai_news_collector_lib",
  "dry_run": true
}
```

2. 执行 Skill：

```bash
python .trae/skills/pypi-release-pipeline/scripts/release_skill.py --request-file .trae/skills/pypi-release-pipeline/examples/release-request.json
```

3. 预期输出（节选）：

```json
{
  "version": "0.1.6",
  "tag": "v0.1.6",
  "status": "success",
  "steps": [
    {"name": "verify_required_env", "status": "success"},
    {"name": "validate_git_state", "status": "success"}
  ]
}
```

## 原子步骤定义

| 步骤 | 输入 | 输出 | 超时 | 重试 | 失败处理 | 回滚 |
|---|---|---|---:|---:|---|---|
| validate_release_request | `version, repo_root, rollback` | 参数验证结果 | 30s | 0 | 直接失败 | 无 |
| verify_required_env | `required_env_vars` | 缺失变量列表/通过 | 30s | 2 | 命令失败返回 `command_error` | 无 |
| validate_git_state | 仓库路径 | 工作区状态 | 60s | 2 | 标记失败 | 无 |
| validate_release_docs | `documentation_gate` | 文档完整性校验结果 | 90s | 2 | 标记失败 | 无 |
| run_tests | 测试命令 | 测试日志 | 600s | 2 | 标记失败 | 无 |
| run_lint | lint 命令 | lint 日志 | 300s | 2 | 标记失败 | 无 |
| run_typecheck | typecheck 命令 | 类型检查日志 | 300s | 2 | 标记失败 | 无 |
| sync_version_files | `version` | 更新文件列表 | 120s | 2 | 标记失败 | 可通过 git reset 回滚 |
| create_release_commit | `version` | commit 结果 | 120s | 2 | 标记失败 | `git reset --hard HEAD~1` |
| create_annotated_tag | `tag` | tag 结果 | 60s | 2 | 标记失败 | `git tag -d <tag>` |
| push_branch_and_tag | `branch, tag` | push 结果 | 300s | 2 | 标记失败 | `git push origin :refs/tags/<tag>` |
| verify_release_artifacts | `tag` | 发布验证结果 | 300s | 2 | 标记失败 | 无 |

## 参数说明

- `version`: 必填，SemVer 格式。
- `repo_root`: 必填，仓库绝对路径。
- `dry_run`: 默认 `true`，仅演练命令。
- `quality_gates`: 自定义 test/lint/typecheck 命令。
- `documentation_gate`: 发布文档门禁配置（README、USAGE_GUIDE、CHANGELOG、Release Note）。
- `retry_policy`: `max_attempts`、`backoff_seconds`、`exponential`。
- `timeouts`: 每个步骤独立超时覆盖。
- `rollback`: `enabled` 与 `mode(none|safe|full)`。

### documentation_gate 配置示例

```json
{
  "documentation_gate": {
    "required_files": ["README.md", "USAGE_GUIDE.md", "CHANGELOG.md"],
    "require_release_note": true,
    "release_note_globs": ["RELEASE_NOTES.md", "V*_RELEASE_SUMMARY.md", "docs/releases/*.md"]
  }
}
```

## 密钥与权限

- 必需环境变量：`PYPI_API_TOKEN`
- 可选环境变量：`GITHUB_TOKEN`
- 最小权限：
  - 文件系统读写
  - Git 操作权限
  - GitHub/PyPI 网络访问

## 测试

```bash
python -m pytest .trae/skills/pypi-release-pipeline/tests -v
```

覆盖内容：
- 正常路径：完整 dry-run 成功
- 边界条件：非法版本、重试后成功
- 失败场景：超时失败、推送失败触发回滚

## CI/CD 中注册、升级、下线

注册：

```bash
python .trae/skills/pypi-release-pipeline/scripts/lifecycle.py register --target-dir .agents/skills
```

升级：

```bash
python .trae/skills/pypi-release-pipeline/scripts/lifecycle.py upgrade --version 1.1.0
```

下线：

```bash
python .trae/skills/pypi-release-pipeline/scripts/lifecycle.py deprecate
```

可在流水线中串联执行：
- PR 合并后自动 register
- 发布分支触发 upgrade
- EOL 分支触发 deprecate

## FAQ

Q: 为什么默认 `dry_run=true`？  
A: 防止误发布，先确保流程可执行与日志完整。

Q: `safe` 和 `full` 回滚区别？  
A: `safe` 不执行 `git reset --hard`，`full` 会追加撤销发布提交。

Q: 如何确保下次调用零配置？  
A: 将默认请求模板固定在 `examples/release-request.json`，在 CI 中预置必要环境变量。
