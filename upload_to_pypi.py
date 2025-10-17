#!/usr/bin/env python3
"""
PyPI上传脚本 - 避免终端Unicode问题
"""
import os
import sys
import subprocess
import shutil
from dotenv import load_dotenv

# 自动加载项目根目录 .env（如果存在），便于读取 TWINE_PASSWORD 等环境变量
load_dotenv()

def upload_to_pypi():
    """上传包到PyPI"""
    print("开始上传到PyPI...")
    
    # 设置环境变量
    # 注意: TWINE_PASSWORD 应该从环境变量中读取，不要硬编码在代码中
    # 使用方法: 在运行前设置环境变量 TWINE_PASSWORD
    if 'TWINE_PASSWORD' not in os.environ:
        print("错误: 未设置 TWINE_PASSWORD 环境变量")
        print("请先设置: export TWINE_PASSWORD='your-pypi-token'")
        return False
    
    # 使用环境中的代理配置（如果需要），不强制设置本地代理
    # 如需代理，请在运行前设置 HTTPS_PROXY 环境变量
    os.environ['TWINE_USERNAME'] = '__token__'
    
    # 检查包文件
    dist_dir = 'dist'
    if not os.path.exists(dist_dir):
        print("错误: dist目录不存在")
        return False

    # 读取当前版本，便于仅上传对应版本的制品
    current_version = None
    try:
        from ai_news_collector_lib import __version__ as _v
        current_version = _v
    except Exception:
        pass

    # 获取包文件列表
    package_files = []
    for file in os.listdir(dist_dir):
        if not file.endswith(('.whl', '.tar.gz')):
            continue
        if current_version and (f"-{current_version}" not in file):
            # 跳过与当前版本不匹配的旧制品，避免 PyPI "File already exists"
            continue
        package_files.append(os.path.join(dist_dir, file))
    
    if not package_files:
        print("错误: 没有找到包文件")
        return False
    
    print(f"找到包文件: {package_files}")
    
    # 构建twine命令
    cmd = [sys.executable, '-m', 'twine', 'upload'] + package_files

    try:
        print("执行上传命令...")
        # 在Windows中文环境下，强制子进程使用UTF-8，避免 rich/twine 输出引发 gbk 编码错误
        child_env = os.environ.copy()
        child_env.setdefault('PYTHONIOENCODING', 'utf-8')
        child_env.setdefault('PYTHONUTF8', '1')
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=child_env
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 上传成功!")
            return True
        else:
            print(f"❌ 上传失败，返回码: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ 上传过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = upload_to_pypi()
    if success:
        print("\n✅ 包已成功上传到PyPI!")
        print("你可以通过以下命令安装:")
        print("pip install ai-news-collector-lib")
    else:
        print("\n❌ 上传失败，请检查错误信息")
        sys.exit(1)
