@echo off
chcp 65001 >nul
echo ================================================
echo   企业文献智能整理多Agent系统 - 快速启动
echo ================================================
echo.

echo [1/3] 检查依赖...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo   正在安装依赖...
    pip install -r requirements.txt -q
    echo   依赖安装完成
)

echo.
echo [2/3] 检查API配置...
findstr /C "your-api-key" config\settings.py >nul
if not errorlevel 1 (
    echo   警告: 请在 config\settings.py 中设置您的 OpenAI API Key
)

echo.
echo [3/3] 启动服务...
echo.
echo ================================================
echo   选择启动模式:
echo ================================================
echo   1. 命令行交互模式
echo   2. Web界面模式
echo   0. 退出
echo ================================================
echo.

set /p choice=请选择 [0-2]:

if "%choice%"=="1" goto cli
if "%choice%"=="2" goto web
if "%choice%"=="0" goto end

:cli
echo 启动命令行模式...
python main.py
goto end

:web
echo 启动Web界面模式...
echo API地址: http://localhost:5000
echo 访问地址: http://localhost:5000
echo.
start http://localhost:5000
python -m api.app
goto end

:end
pause