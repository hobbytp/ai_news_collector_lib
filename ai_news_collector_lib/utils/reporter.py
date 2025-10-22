"""
报告生成器
用于生成各种格式的报告
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""

    def __init__(self, output_dir: str = "./reports"):
        """
        初始化报告生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Report generator initialized with output directory: {self.output_dir}")

    def generate_daily_report(self, result: Dict[str, Any], format: str = "markdown") -> str:
        """
        生成每日报告

        Args:
            result: 收集结果
            format: 报告格式 (markdown, html, json)

        Returns:
            str: 报告内容
        """
        if format == "markdown":
            return self._generate_markdown_report(result)
        elif format == "html":
            return self._generate_html_report(result)
        elif format == "json":
            return self._generate_json_report(result)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown_report(self, result: Dict[str, Any]) -> str:
        """生成Markdown报告"""
        date_str = datetime.now().strftime("%Y年%m月%d日")

        report = f"""# AI信息搜集日报 - {date_str}

## 📊 收集统计
- **总文章数**: {result.get('total_articles', 0)}
- **独特文章数**: {result.get('unique_articles', 0)}
- **去重数量**: {result.get('duplicates_removed', 0)}
- **总字数**: {result.get('total_words', 0):,}
- **平均阅读时间**: {result.get('average_reading_time', 0)} 分钟
- **收集耗时**: {result.get('collection_duration', 0):.1f} 秒

## 🔍 主题统计
"""

        # 添加主题统计
        topic_results = result.get("topic_results", {})
        for topic, stats in topic_results.items():
            if "error" in stats:
                report += f"- **{topic}**: ❌ 收集失败 - {stats['error']}\n"
            else:
                report += f"- **{topic}**: ✅ {stats.get('unique', 0)} 篇独特文章\n"

        report += f"""
## 📰 热门文章 (前10篇)
"""

        # 添加热门文章
        articles = result.get("articles", [])
        for i, article in enumerate(articles[:10], 1):
            report += f"{i}. [{article.get('title', 'No title')}]({article.get('url', '#')})\n"
            report += f"   - 来源: {article.get('source_name', 'Unknown')}\n"
            report += f"   - 阅读时间: {article.get('reading_time', 0)} 分钟\n"
            if article.get("keywords"):
                report += f"   - 关键词: {', '.join(article['keywords'][:3])}\n"
            report += "\n"

        return report

    def _generate_html_report(self, result: Dict[str, Any]) -> str:
        """生成HTML报告"""
        date_str = datetime.now().strftime("%Y年%m月%d日")

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI信息搜集日报 - {date_str}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; }}
        .articles {{ margin-top: 30px; }}
        .article {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .article h3 {{ margin-top: 0; }}
        .article-meta {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI信息搜集日报 - {date_str}</h1>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>总文章数</h3>
            <p>{result.get('total_articles', 0)}</p>
        </div>
        <div class="stat-card">
            <h3>独特文章数</h3>
            <p>{result.get('unique_articles', 0)}</p>
        </div>
        <div class="stat-card">
            <h3>去重数量</h3>
            <p>{result.get('duplicates_removed', 0)}</p>
        </div>
        <div class="stat-card">
            <h3>总字数</h3>
            <p>{result.get('total_words', 0):,}</p>
        </div>
        <div class="stat-card">
            <h3>平均阅读时间</h3>
            <p>{result.get('average_reading_time', 0)} 分钟</p>
        </div>
    </div>
    
    <div class="articles">
        <h2>热门文章</h2>
"""

        # 添加文章列表
        articles = result.get("articles", [])
        for i, article in enumerate(articles[:10], 1):
            html += f"""
        <div class="article">
            <h3>{i}. {article.get('title', 'No title')}</h3>
            <div class="article-meta">
                <p>来源: {article.get('source_name', 'Unknown')} | 
                   阅读时间: {article.get('reading_time', 0)} 分钟</p>
                <p>关键词: {', '.join(article.get('keywords', [])[:3])}</p>
            </div>
            <p><a href="{article.get('url', '#')}" target="_blank">阅读原文</a></p>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""

        return html

    def _generate_json_report(self, result: Dict[str, Any]) -> str:
        """生成JSON报告"""
        return json.dumps(result, ensure_ascii=False, indent=2)

    def save_report(
        self, result: Dict[str, Any], filename: Optional[str] = None, format: str = "markdown"
    ) -> str:
        """
        保存报告到文件

        Args:
            result: 收集结果
            filename: 文件名，None自动生成
            format: 报告格式

        Returns:
            str: 保存的文件路径
        """
        # 生成报告内容
        report_content = self.generate_daily_report(result, format)

        # 生成文件名
        if filename is None:
            date_str = datetime.now().strftime("%Y%m%d")
            ext = format if format != "markdown" else "md"
            filename = f"daily_report_{date_str}.{ext}"

        # 保存文件
        file_path = self.output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"Report saved to: {file_path}")
        return str(file_path)

    def generate_summary_report(self, results: List[Dict[str, Any]], days: int = 7) -> str:
        """
        生成汇总报告

        Args:
            results: 多天结果列表
            days: 天数

        Returns:
            str: 汇总报告
        """
        if not results:
            return "没有数据生成汇总报告"

        # 统计汇总数据
        total_articles = sum(r.get("total_articles", 0) for r in results)
        total_unique = sum(r.get("unique_articles", 0) for r in results)
        total_words = sum(r.get("total_words", 0) for r in results)
        avg_reading_time = sum(r.get("average_reading_time", 0) for r in results) / len(results)

        # 统计各源使用情况
        source_stats = {}
        for result in results:
            articles = result.get("articles", [])
            for article in articles:
                source = article.get("source", "unknown")
                source_stats[source] = source_stats.get(source, 0) + 1

        # 生成汇总报告
        report = f"""# AI信息搜集周报

## 📊 汇总统计 ({days}天)
- **总文章数**: {total_articles:,}
- **独特文章数**: {total_unique:,}
- **总字数**: {total_words:,}
- **平均阅读时间**: {avg_reading_time:.1f} 分钟

## 📈 各源使用情况
"""

        for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{source}**: {count} 篇文章\n"

        report += f"""
## 📅 每日统计
"""

        for i, result in enumerate(results, 1):
            date = result.get("collection_time", "Unknown")
            report += f"- **第{i}天**: {result.get('unique_articles', 0)} 篇独特文章\n"

        return report
