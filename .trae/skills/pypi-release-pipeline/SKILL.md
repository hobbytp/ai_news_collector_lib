---
name: pypi-release-pipeline
description: Orchestrates Python library release to PyPI and GitHub with validation, retries, rollback, and CI/CD lifecycle automation. Use when publishing, upgrading, or retiring a release workflow skill.
license: Apache-2.0
compatibility: Python 3.9+, git, network access to GitHub/PyPI, read-write access to repository and CI configs.
metadata:
  author: AI News Collector Team
  version: "1.1.0"
  spec: "agentskills.io"
  runtime: "python"
  quality_gate: "unit,integration,lint,typecheck"
  secrets: "PYPI_API_TOKEN,GITHUB_TOKEN"
  config_file: "skill.yaml"
  input_schema: "assets/release-request.schema.json"
  metadata_schema: "assets/skill-metadata.schema.json"
---

# PyPI Release Pipeline Skill

## 何时使用

当用户要求执行或标准化以下任务时启用本 Skill：
- 发布 Python 包到 PyPI
- 基于 Git Tag 触发 GitHub Release
- 将发布流程拆解为可重复执行的原子步骤
- 在 CI/CD 中注册、升级、下线发布 Skill

## 输入契约

严格遵循 `assets/release-request.schema.json`：
- `version`: 目标发布版本，必须符合 SemVer
- `repo_root`: 仓库路径
- `dry_run`: 是否只演练不实际推送
- `documentation_gate`: 文档门禁配置（README、USAGE_GUIDE、CHANGELOG、Release Note）
- `retry_policy`: 全局重试策略
- `timeouts`: 原子步骤超时策略
- `rollback`: 回滚开关与模式

## 原子步骤与执行顺序

1. `validate_release_request`
2. `verify_required_env`
3. `validate_git_state`
4. `validate_release_docs`
5. `run_quality_gates`
6. `sync_version_files`
7. `create_release_commit`
8. `create_annotated_tag`
9. `push_branch_and_tag`
10. `verify_ci_publication`
11. `verify_release_artifacts`

每个步骤都输出结构化结果：
- `status`: `success|failed|skipped`
- `started_at` / `ended_at`
- `attempts`
- `stdout` / `stderr`
- `rollback_actions`

## 超时与重试

- 默认重试：最多 2 次，指数退避
- 默认超时：
  - 轻量校验步骤 30~120 秒
  - 构建/发布步骤 300~900 秒
- 任一步骤失败时根据 `rollback.mode` 执行回滚：
  - `none`
  - `safe`（仅删除 tag、还原临时文件）
  - `full`（在 safe 基础上撤销发布提交）

## 异常处理与回滚

- 命令超时：标记 `timeout_error` 并按重试策略重试
- 命令退出码非零：标记 `command_error`
- 参数校验错误：立即失败，不进入后续步骤
- 回滚失败：保留失败记录并继续执行剩余可执行回滚动作

## 使用入口

- 实现代码：`src/release_skill/orchestrator.py`
- CLI 入口：`scripts/release_skill.py`
- 生命周期管理：`scripts/lifecycle.py`
- 示例：`examples/invoke_release_skill.py`
- 文档：`README.md`

## 质量门禁

执行前后应通过：
- 单元测试：`tests/test_release_skill_unit.py`
- 集成测试：`tests/test_release_skill_integration.py`
- Lint：`make lint`
- Typecheck：`python -m mypy .trae/skills/pypi-release-pipeline/src`
