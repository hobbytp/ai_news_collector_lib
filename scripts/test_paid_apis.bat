@echo off
REM 付费API测试快速运行脚本 (Windows版本)

setlocal enabledelayedexpansion

cd /d "%~dp0.."

echo ==========================================
echo   付费API测试工具
echo ==========================================
echo.

REM 检查 .env 文件
if not exist ".env" (
    echo [91m警告: .env 文件不存在[0m
    echo.
    echo 请创建 .env 文件并配置API密钥：
    echo   copy env.example .env
    echo.
    pause
    exit /b 1
)

REM 检查cassettes数量
set CASSETTE_COUNT=0
if exist "tests\cassettes" (
    for %%f in (tests\cassettes\*.yaml) do set /a CASSETTE_COUNT+=1
)

echo [92m当前状态：[0m
echo   Cassette文件: !CASSETTE_COUNT! 个
echo.

:menu
echo 请选择操作：
echo.
echo   [1] 首次录制 - 运行付费API测试并录制HTTP请求（消耗少量API配额）
echo   [2] 离线测试 - 使用现有cassettes运行（完全免费）
echo   [3] 重新录制 - 删除旧cassettes并重新录制
echo   [4] 查看覆盖率 - 运行测试并生成覆盖率报告
echo   [5] 仅测试特定API
echo   [0] 退出
echo.

set /p choice="请输入选项 [0-5]: "

if "%choice%"=="1" goto first_record
if "%choice%"=="2" goto offline_test
if "%choice%"=="3" goto re_record
if "%choice%"=="4" goto coverage
if "%choice%"=="5" goto specific_api
if "%choice%"=="0" goto end

echo [91m无效选项[0m
goto menu

:first_record
echo.
echo [96m开始首次录制...[0m
echo.

findstr /c:"ALLOW_NETWORK=1" .env >nul
if errorlevel 1 (
    echo [91m警告: 请在 .env 中设置 ALLOW_NETWORK=1[0m
    pause
    exit /b 1
)

findstr /c:"TEST_PAID_APIS=1" .env >nul
if errorlevel 1 (
    echo [91m警告: 请在 .env 中设置 TEST_PAID_APIS=1[0m
    pause
    exit /b 1
)

echo [92m环境配置正确[0m
echo.
echo [93m注意：这将消耗少量API配额（约 ^<$0.01）[0m
echo.
set /p confirm="确认继续? [y/N] "
if /i not "%confirm%"=="y" (
    echo 已取消
    goto end
)

python -m pytest tests/test_paid_apis.py -v

echo.
echo [92m录制完成！后续可以离线运行测试[0m
pause
goto end

:offline_test
echo.
echo [96m运行离线测试...[0m
echo.

if !CASSETTE_COUNT! equ 0 (
    echo [91m错误：没有找到cassette文件[0m
    echo.
    echo 请先运行选项1进行首次录制
    pause
    exit /b 1
)

python -m pytest tests/test_paid_apis.py -v

echo.
echo [92m测试完成！完全使用cassette回放，零API消耗[0m
pause
goto end

:re_record
echo.
echo [96m重新录制cassettes...[0m
echo.

if !CASSETTE_COUNT! gtr 0 (
    set /p confirm="确认删除 !CASSETTE_COUNT! 个现有cassettes? [y/N] "
    if /i not "!confirm!"=="y" (
        echo 已取消
        goto end
    )
    
    del /q tests\cassettes\*.yaml 2>nul
    echo [92m已删除旧cassettes[0m
)

set UPDATE_CASSETTES=1
python -m pytest tests/test_paid_apis.py -v

echo.
echo [92m重新录制完成！[0m
pause
goto end

:coverage
echo.
echo [96m生成覆盖率报告...[0m
echo.

python -m pytest tests/test_paid_apis.py --cov=ai_news_collector_lib --cov-report=term-missing --cov-report=html -v

echo.
echo [92m覆盖率报告已生成[0m
echo.
echo [93m查看详细报告：[0m
echo   htmlcov\index.html
echo.
pause
goto end

:specific_api
echo.
echo 可用的API测试：
echo.
echo   [1] Tavily
echo   [2] Google Search
echo   [3] Serper
echo   [4] Brave Search
echo   [5] MetaSota
echo   [6] NewsAPI
echo.
set /p api_choice="请输入API编号 [1-6]: "

if "%api_choice%"=="1" set TEST_NAME=test_tavily_search
if "%api_choice%"=="2" set TEST_NAME=test_google_search
if "%api_choice%"=="3" set TEST_NAME=test_serper_search
if "%api_choice%"=="4" set TEST_NAME=test_brave_search
if "%api_choice%"=="5" set TEST_NAME=test_metasota_search
if "%api_choice%"=="6" set TEST_NAME=test_newsapi_search

if not defined TEST_NAME (
    echo [91m无效选项[0m
    pause
    goto end
)

echo.
echo [96m运行测试: %TEST_NAME%[0m
echo.

python -m pytest tests/test_paid_apis.py::%TEST_NAME% -v

pause
goto end

:end
echo.
echo ==========================================
echo   完成
echo ==========================================
