@echo off
chcp 65001 >nul
echo ========================================
echo   校园网自动登录工具 - 安装脚本
echo ========================================
echo.

REM 检查Python是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "python_version=%%i"
echo 检测到Python版本: %python_version%

REM 安装依赖
echo.
echo [1/4] 安装Python依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [警告] 依赖安装可能有问题，请手动检查
)

REM 创建配置文件
echo.
echo [2/4] 创建配置文件...
if not exist "config.ini" (
    copy "config.ini.template" "config.ini" >nul
    echo 已创建配置文件: config.ini
    echo 请编辑此文件配置账号密码和路径
) else (
    echo 配置文件已存在: config.ini
)

REM 创建日志目录
echo.
echo [3/4] 创建日志目录...
if not exist "logs" mkdir logs
echo 日志目录: logs\

REM 运行设置向导
echo.
echo [4/4] 运行设置向导...
echo 请按照提示配置账号密码和路径
echo.
python main.py --setup

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 使用说明:
echo   1. 测试运行: python main.py
echo   2. 调试模式: python main.py --debug
echo   3. 查看帮助: python main.py --help
echo.
echo 开机自启动设置:
echo   1. 将本工具添加到计划任务
echo   2. 或复制快捷方式到启动文件夹
echo.
pause