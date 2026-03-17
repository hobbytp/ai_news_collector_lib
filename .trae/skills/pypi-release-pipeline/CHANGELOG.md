# Changelog

## 1.1.0 - 2026-03-17

- 新增发布文档门禁步骤 `validate_release_docs`
- 新增文档校验脚本 `verify_release_docs.py`
- 发布前默认强制检查 `README.md`、`USAGE_GUIDE.md`、`CHANGELOG.md` 与 Release Note
- 扩展 `release-request.schema.json`，新增 `documentation_gate` 配置
- 更新 `README.md`、`SKILL.md`、`skill.yaml` 与示例请求
- 更新单元测试与集成测试，覆盖新增步骤与默认参数

## 1.0.0 - 2026-03-17

- 新增符合 `agentskills.io` 规范的 `SKILL.md` 与元数据 frontmatter
- 新增 `skill.yaml` 与配套 JSON Schema（元数据与请求入参）
- 新增发布编排核心实现，覆盖原子步骤、重试、超时、异常、回滚
- 新增生命周期脚本，支持注册、升级、下线
- 新增单元测试与集成测试
- 新增调用示例与文档（快速开始、参数说明、FAQ、CI/CD 指南）
