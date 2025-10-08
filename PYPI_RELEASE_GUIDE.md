# PyPI发布指南

## 🚀 发布ai_news_collector_lib到PyPI

### 当前状态

- ✅ 包构建成功
- ✅ 包检查通过
- ⚠️ 需要设置PyPI认证信息

### 步骤1: 创建PyPI账户

1. 访问 [PyPI官网](https://pypi.org/)
2. 点击 "Register" 创建账户
3. 验证邮箱地址

### 步骤2: 创建API Token

1. 登录PyPI账户
2. 进入 "Account Settings" > "API tokens"
3. 点击 "Add API token"
4. 选择 "Entire account" 或 "Specific project"
5. 复制生成的API token（格式：`pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）

### 步骤3: 设置认证信息

#### 方法1: 使用环境变量（推荐）

```bash
# Windows (Git Bash)
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-your-api-token-here"

# Windows PowerShell
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-your-api-token-here"
```

#### 方法2: 使用配置文件

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token-here
```

### 步骤4: 发布到PyPI

#### 先发布到测试PyPI（推荐）

```bash
# 设置测试PyPI认证
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-your-testpypi-token-here"

# 上传到测试PyPI
twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ ai-news-collector-lib
```

#### 发布到正式PyPI

```bash
# 设置正式PyPI认证
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-your-api-token-here"

# 上传到正式PyPI
twine upload dist/*
```

### 步骤5: 验证发布

1. 访问 [PyPI项目页面](https://pypi.org/project/ai-news-collector-lib/)
2. 测试安装：

   ```bash
   pip install ai-news-collector-lib
   ```

3. 测试导入：

   ```python
   import ai_news_collector_lib
   print(ai_news_collector_lib.__version__)
   ```

### 故障排除

#### 1. 认证失败

- 检查API token是否正确
- 确保token有足够的权限
- 检查用户名是否为 `__token__`

#### 2. 网络超时

- 检查网络连接
- 尝试使用VPN
- 稍后重试

#### 3. 包名冲突

- 检查包名是否已被占用
- 考虑更改包名
- 联系PyPI管理员

#### 4. 包大小限制

- PyPI有包大小限制
- 检查包是否过大
- 优化包内容

### 发布后维护

1. **版本管理**
   - 更新 `pyproject.toml` 中的版本号
   - 更新 `__init__.py` 中的版本号
   - 重新构建和发布

2. **文档更新**
   - 更新README.md
   - 更新CHANGELOG.md
   - 更新文档网站

3. **用户支持**
   - 监控GitHub Issues
   - 回复用户问题
   - 收集用户反馈

### 自动化发布

可以使用GitHub Actions自动发布：

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

### 安全注意事项

1. **保护API Token**
   - 不要将token提交到代码仓库
   - 使用环境变量或密钥管理
   - 定期轮换token

2. **验证包内容**
   - 检查包是否包含敏感信息
   - 确保不包含恶意代码
   - 验证依赖项的安全性

---

**下一步**: 请按照上述步骤设置PyPI认证，然后重新运行发布命令。
