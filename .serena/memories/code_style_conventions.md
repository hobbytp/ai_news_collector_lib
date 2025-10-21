# 代码风格和约定

## Python 版本和标准

- **最低版本**: Python 3.8
- **目标版本**: Python 3.8, 3.9, 3.10, 3.11
- **代码编码**: UTF-8
- **代码格式**: Black (line-length: 88)

## 代码风格

### 代码格式化

**工具**: Black  
**配置**:
```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
```

### 类型提示

**要求**: 所有函数和方法都应使用完整的类型提示

示例：
```python
def search(self, query: str, days_back: int = 7) -> List[Article]:
    """执行搜索"""
    pass

async def collect_news(self, query: str) -> SearchResult:
    """收集新闻"""
    pass
```

### 文档字符串

**格式**: Google 风格的文档字符串

示例：
```python
def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
    """从文本中提取关键词。
    
    Args:
        text: 输入文本
        max_keywords: 最多提取的关键词数量
        
    Returns:
        关键词列表
        
    Raises:
        ValueError: 如果文本为空
    """
    pass
```

### 异步代码

- 使用 `async`/`await` 语法
- 异步函数以 `async def` 开头
- 优先使用异步操作：`aiohttp` 而不是 `requests`

示例：
```python
async def collect_news(self, query: str) -> SearchResult:
    """异步收集新闻"""
    tasks = [
        self.tools['hackernews'].search(query),
        self.tools['arxiv'].search(query),
    ]
    results = await asyncio.gather(*tasks)
    return self._aggregate_results(results)
```

## 命名约定

### 模块和文件
- 小写字母和下划线
- 例：`search_tools.py`、`content_extractor.py`

### 类名
- PascalCase（大驼峰）
- 例：`Article`、`AINewsCollector`、`AdvancedArticle`

### 函数/方法名
- snake_case（小写下划线）
- 私有方法以单个下划线开头
- 例：`collect_news()`、`_aggregate_results()`

### 常量
- UPPER_SNAKE_CASE
- 例：`DEFAULT_MAX_ARTICLES = 10`

### 变量名
- snake_case
- 例：`max_articles`、`is_enabled`

## 数据建模

### 使用 dataclass

- 使用 `@dataclass` 装饰器定义数据模型
- 使用类型提示
- 提供 `to_dict()` 和 `from_dict()` 方法进行序列化

示例：
```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Article:
    title: str
    url: str
    summary: str
    published: str
    author: str
    source_name: str
    source: str
    content: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {...}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        """从字典创建实例"""
        return cls(...)
```

## 导入规则

### 导入顺序
1. 标准库导入
2. 第三方导入
3. 本地导入

示例：
```python
import asyncio
import logging
from dataclasses import dataclass
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .models import Article
from ..config import SearchConfig
```

### 避免 import *
- 使用显式导入
- 不要使用 `from module import *`

## 错误处理

### 异常处理

- 使用特定的异常类型
- 提供有意义的错误信息
- 记录异常到日志

示例：
```python
import logging

logger = logging.getLogger(__name__)

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"Failed to fetch {url}: {e}")
    raise ValueError(f"Invalid URL or network error: {e}")
```

## 日志

### 日志配置

```python
import logging

# 获取模块日志记录器
logger = logging.getLogger(__name__)

# 使用不同的日志级别
logger.debug("调试信息")
logger.info("信息")
logger.warning("警告")
logger.error("错误")
```

### 日志级别

- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

## 代码注释

### 注释原则
- 解释 "为什么"，而不是 "是什么"
- 保持注释简洁
- 更新代码时同时更新注释

### 示例

```python
# ✓ 好的注释
# 使用 similarity_threshold 避免收集过多重复内容
duplicates = remove_duplicates(articles, threshold=0.85)

# ✗ 不好的注释
# 移除重复
duplicates = remove_duplicates(articles, threshold=0.85)
```

## Optional 导入处理

某些依赖是可选的（如 `schedule` 模块）。使用以下模式：

```python
try:
    from .utils.scheduler import DailyScheduler
except ImportError:
    DailyScheduler = None
```

在导出时：
```python
if DailyScheduler is not None:
    __all__.insert(-3, 'DailyScheduler')
```

## 验证器（Validators）

使用 `__post_init__` 进行数据验证和处理：

```python
@dataclass
class Article:
    def __post_init__(self):
        """初始化后处理和验证"""
        if self.published and not self.published.endswith('Z') and 'T' in self.published:
            try:
                dt = datetime.fromisoformat(self.published.replace('Z', '+00:00'))
                self.published = dt.isoformat()
            except ValueError:
                pass
```

## 类型检查

**工具**: mypy

配置示例：
```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
```

命令：
```bash
mypy ai_news_collector_lib --strict
```

## 性能建议

1. **异步优先**: 使用 `async`/`await` 进行并发操作
2. **连接复用**: 使用连接池（aiohttp 默认支持）
3. **缓存**: 避免重复搜索，使用缓存
4. **流式处理**: 大文件使用流式处理
5. **资源清理**: 使用上下文管理器（with/async with）

## 配置最佳实践

1. **使用 dataclass 管理配置**
2. **提供合理的默认值**
3. **支持从环境变量加载**
4. **验证配置值**

示例：
```python
@dataclass
class SearchConfig:
    enable_hackernews: bool = True
    enable_arxiv: bool = True
    max_articles_per_source: int = 10
    days_back: int = 7
```

## 单元测试风格

- 使用 pytest
- 异步测试使用 `@pytest.mark.asyncio`
- 测试函数名以 `test_` 开头
- 使用 mock 隔离外部依赖

示例：
```python
@pytest.mark.asyncio
async def test_collect_news():
    config = SearchConfig()
    collector = AINewsCollector(config)
    result = await collector.collect_news("test")
    assert result is not None
```
