# 项目架构和扩展指南

## 核心架构层次

### 1. Core Layer (核心层)

**位置**: `ai_news_collector_lib/core/`

**主要类**:
- `AINewsCollector`: 基础搜集器，管理搜索工具和协调搜索
- `AdvancedAINewsCollector`: 继承自 `AINewsCollector`，增加内容提取、关键词分析、缓存

**职责**:
- 初始化和管理搜索工具
- 协调多个搜索源的并行搜索
- 实现结果去重
- 提供公共 API

**关键方法**:
- `collect_news(query, sources)`: 基础搜集
- `collect_news_advanced(query)`: 高级搜集（内容提取、关键词分析）
- `_aggregate_results()`: 合并来自多个源的结果
- `_remove_duplicates()`: 去除重复文章

### 2. Data Layer (数据层)

**位置**: `ai_news_collector_lib/models/`

**主要类**:
- `Article`: 基础文章数据结构
- `AdvancedArticle`: 增强文章（包含关键词、情感、阅读时间等）
- `SearchResult`: 搜索结果聚合

**特点**:
- 使用 `@dataclass` 装饰器
- 提供 `to_dict()` 和 `from_dict()` 方法
- 使用 `__post_init__()` 进行初始化后处理

### 3. Tools Layer (工具层)

**位置**: `ai_news_collector_lib/tools/search_tools.py`

**基类**:
- `BaseSearchTool`: 所有搜索工具的基类

**已实现的工具**:
- `HackerNewsTool`: HackerNews
- `ArxivTool`: ArXiv（含日期解析和 feedparser 回退）
- `DuckDuckGoTool`: DuckDuckGo
- `NewsAPITool`: NewsAPI
- 其他：TavilyTool、GoogleSearchTool、BingSearchTool 等

**搜索工具接口**:
```python
class BaseSearchTool:
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """执行搜索"""
        raise NotImplementedError
```

### 4. Utils Layer (工具层)

**位置**: `ai_news_collector_lib/utils/`

**主要模块**:
- `cache.py`: `CacheManager` - 结果缓存管理
- `content_extractor.py`: `ContentExtractor` - 网页内容提取
- `keyword_extractor.py`: `KeywordExtractor` - 关键词提取
- `reporter.py`: `ReportGenerator` - 报告生成
- `scheduler.py`: `DailyScheduler` - 定时任务调度

### 5. Config Layer (配置层)

**位置**: `ai_news_collector_lib/config/settings.py`

**主要类**:
- `SearchConfig`: 基础搜索配置（启用/禁用搜索源、参数设置）
- `AdvancedSearchConfig`: 扩展配置（内容提取、缓存等）

## 数据流

```
User Query
    ↓
SearchConfig 创建
    ↓
AINewsCollector 初始化
    ↓
Tools 初始化
    ↓
并行搜索执行 (多个搜索源)
    ↓
结果收集
    ↓
去重处理
    ↓
内容提取 (高级模式)
    ↓
关键词分析 (高级模式)
    ↓
缓存存储 (高级模式)
    ↓
返回 SearchResult
```

## 关键设计模式

### 1. 工厂模式 (Factory Pattern)

搜索工具通过工厂方法初始化：
```python
def _initialize_tools(self):
    """初始化搜索工具"""
    if self.config.enable_hackernews:
        self.tools['hackernews'] = HackerNewsTool(max_articles=self.config.max_articles_per_source)
    # ... 其他工具
```

### 2. 模板方法模式 (Template Method Pattern)

`BaseSearchTool` 定义了搜索的基本流程，子类实现具体的搜索逻辑：
```python
class BaseSearchTool:
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        raise NotImplementedError

class HackerNewsTool(BaseSearchTool):
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        # HackerNews 特定的搜索实现
        pass
```

### 3. 策略模式 (Strategy Pattern)

通过配置选择不同的功能策略：
- `enable_content_extraction`: 是否提取内容
- `enable_keyword_extraction`: 是否提取关键词
- `cache_results`: 是否缓存结果

### 4. 装饰器模式 (Decorator Pattern)

`AdvancedAINewsCollector` 装饰基础收集器，添加额外功能：
```python
class AdvancedAINewsCollector(AINewsCollector):
    def __init__(self, config: AdvancedSearchConfig):
        super().__init__(config)
        self.content_extractor = ContentExtractor()
        self.keyword_extractor = KeywordExtractor()
```

## 扩展指南

### 添加新的搜索源

#### 步骤 1: 创建搜索工具类

在 `ai_news_collector_lib/tools/search_tools.py` 中添加：

```python
class CustomSearchTool(BaseSearchTool):
    """自定义搜索工具"""
    
    def __init__(self, api_key: str = None, max_articles: int = 10):
        super().__init__(max_articles)
        self.api_key = api_key or os.getenv('CUSTOM_API_KEY')
        self.base_url = 'https://api.custom.com'
    
    def search(self, query: str, days_back: int = 7) -> List[Article]:
        """执行搜索"""
        try:
            # 1. 构建请求
            params = {
                'q': query,
                'limit': self.max_articles,
                'api_key': self.api_key
            }
            
            # 2. 发送请求
            response = requests.get(f'{self.base_url}/search', params=params, timeout=10)
            response.raise_for_status()
            
            # 3. 解析响应
            data = response.json()
            
            # 4. 转换为 Article 对象
            articles = []
            for item in data.get('results', []):
                article = Article(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    summary=item.get('description', ''),
                    published=item.get('published_date', ''),
                    author=item.get('author', ''),
                    source_name='CustomSearch',
                    source='custom'
                )
                articles.append(article)
            
            return articles[:self.max_articles]
        except Exception as e:
            logger.error(f"CustomSearch 搜索失败: {e}")
            return []
```

#### 步骤 2: 在配置中添加选项

在 `ai_news_collector_lib/config/settings.py` 中：

```python
@dataclass
class SearchConfig:
    # ... 现有配置
    enable_custom_search: bool = False
    custom_search_api_key: Optional[str] = None
```

#### 步骤 3: 在收集器中初始化工具

在 `ai_news_collector_lib/core/collector.py` 的 `_initialize_tools()` 中：

```python
if self.config.enable_custom_search:
    self.tools['custom_search'] = CustomSearchTool(
        api_key=self.config.custom_search_api_key,
        max_articles=self.config.max_articles_per_source
    )
```

#### 步骤 4: 添加测试

在 `ai_news_collector_lib/tests/test_*.py` 或 `tests/` 中添加测试。

### 添加新的内容处理器

#### 步骤 1: 创建处理器类

```python
# ai_news_collector_lib/utils/custom_processor.py

class CustomProcessor:
    """自定义内容处理器"""
    
    def process(self, article: Article) -> Article:
        """处理文章"""
        # 处理逻辑
        return article
```

#### 步骤 2: 在高级收集器中集成

```python
class AdvancedAINewsCollector(AINewsCollector):
    def __init__(self, config: AdvancedSearchConfig):
        super().__init__(config)
        self.custom_processor = CustomProcessor()
    
    async def collect_news_advanced(self, query: str) -> Dict[str, Any]:
        # ... 现有逻辑
        for article in result['articles']:
            article = self.custom_processor.process(article)
```

### 添加新的报告格式

#### 步骤 1: 扩展报告生成器

在 `ai_news_collector_lib/utils/reporter.py` 中：

```python
class ReportGenerator:
    def generate_custom_format(self, result: Dict) -> str:
        """生成自定义格式报告"""
        # 生成逻辑
        return report_content
```

## 调用链示例

### 基础使用流程

```
1. 创建配置
   config = SearchConfig(enable_hackernews=True, enable_arxiv=True)

2. 创建收集器
   collector = AINewsCollector(config)
   ↓ 初始化时调用 _initialize_tools()
   ↓ 创建 HackerNewsTool 和 ArxivTool

3. 执行搜集
   result = await collector.collect_news("AI")
   ↓ 获取查询参数
   ↓ 调用 _prepare_search_tasks()
   ↓ 创建异步任务
   ↓ 使用 asyncio.gather() 并行执行
   ↓ 调用每个工具的 search() 方法
   ↓ 收集结果

4. 处理结果
   ↓ 调用 _aggregate_results()
   ↓ 调用 _remove_duplicates()
   ↓ 返回 SearchResult
```

### 高级使用流程

```
1. 创建高级配置
   config = AdvancedSearchConfig(
       enable_content_extraction=True,
       enable_keyword_extraction=True,
       cache_results=True
   )

2. 创建高级收集器
   collector = AdvancedAINewsCollector(config)
   ↓ 初始化父类的工具
   ↓ 初始化 ContentExtractor
   ↓ 初始化 KeywordExtractor
   ↓ 初始化 CacheManager

3. 执行高级搜集
   result = await collector.collect_news_advanced("AI")
   ↓ 检查缓存
   ↓ 执行基础搜集
   ↓ 对每篇文章进行内容提取
   ↓ 对每篇文章进行关键词分析
   ↓ 创建 AdvancedArticle 对象
   ↓ 缓存结果
   ↓ 返回增强结果
```

## 常见扩展场景

### 场景 1: 添加新的搜索源

**步骤**: 创建搜索工具 → 添加配置选项 → 在收集器中初始化 → 添加测试

**文件**: `search_tools.py`, `settings.py`, `collector.py`, `test_*.py`

### 场景 2: 实现新的缓存后端

**步骤**: 扩展 `CacheManager` → 添加新的后端实现（如 Redis）

**文件**: `utils/cache.py`

### 场景 3: 集成新的 NLP 库

**步骤**: 创建新的关键词提取器 → 在 `AdvancedAINewsCollector` 中使用

**文件**: `utils/keyword_extractor.py`, `core/advanced_collector.py`

### 场景 4: 支持新的报告格式

**步骤**: 在 `ReportGenerator` 中添加新的生成方法

**文件**: `utils/reporter.py`

## 模块依赖关系

```
models (数据模型)
    ↑
    ├── core (收集器) ← 使用
    ├── tools (搜索工具) ← 使用
    └── utils (工具函数) ← 使用
        
config (配置)
    ↑
    └── core (收集器) ← 使用
        
tools (搜索工具)
    ↑
    └── core (收集器) ← 使用
        
utils (工具函数)
    ↑
    └── core/advanced_collector ← 使用
```

## 向后兼容性考虑

1. **API 稳定性**
   - 避免改变现有方法的签名
   - 新增功能应该是可选的
   - 使用配置选项而不是强制行为变更

2. **配置兼容性**
   - 提供合理的默认值
   - 支持旧的配置格式（如果必要）
   - 文档记录弃用的配置选项

3. **数据模型兼容性**
   - 使用 `Optional` 字段表示新增字段
   - 在 `from_dict()` 中处理缺失字段
   - 版本化 API 响应

## 性能考虑

1. **异步操作**
   - 优先使用 `async`/`await`
   - 使用 `asyncio.gather()` 进行并发

2. **缓存策略**
   - 使用合理的 TTL（Time To Live）
   - 实现缓存过期机制

3. **资源管理**
   - 限制并发请求数
   - 实现请求超时
   - 释放不需要的资源

4. **错误处理**
   - 实现重试机制
   - 优雅降级（单个源失败不影响整体）
