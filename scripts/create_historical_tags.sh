#!/bin/bash
# 为历史版本创建 Git Tags
# 用法: bash scripts/create_historical_tags.sh

set -e

echo "=== 为历史 PyPI 版本创建 Git Tags ==="
echo ""

# v0.1.0 - Initial commit
echo "创建 v0.1.0 tag..."
git tag -a v0.1.0 bb60748 -m "Release v0.1.0 - Initial release

## Features

- 多源新闻搜索（HackerNews、ArXiv、DuckDuckGo等）
- 内容提取和关键词分析
- 结果去重和缓存
- 定时任务支持
- 灵活的配置系统

## PyPI

https://pypi.org/project/ai-news-collector-lib/0.1.0/
" 2>/dev/null || echo "  → v0.1.0 tag 已存在"

# v0.1.1 - PR #1 merged (ArXiv 修复 + MetaSota 检测)
echo "创建 v0.1.1 tag..."
git tag -a v0.1.1 b83a557 -m "Release v0.1.1 - Bug fixes and improvements

## Bug Fixes

- 修复 ArXiv feedparser 日期回退逻辑
- 修复 ContentExtractor regex 导入问题
- 改进 MetaSota MCP 404/405 检测和处理
- 添加 lxml 依赖

## Documentation

- 同步 ArXiv 日期回退说明至 README 与 USAGE_GUIDE
- 新增最小验证脚本

## PyPI

https://pypi.org/project/ai-news-collector-lib/0.1.1/
" 2>/dev/null || echo "  → v0.1.1 tag 已存在"

echo ""
echo "=== Tags 创建完成 ==="
echo ""
echo "本地 tags:"
git tag -l "v*"
echo ""
echo "推送 tags 到 GitHub:"
echo "  git push origin v0.1.0 v0.1.1"
echo ""
echo "或推送所有 tags:"
echo "  git push origin --tags"
