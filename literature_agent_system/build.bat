@echo off
echo ================================================
echo   企业文献智能整理多Agent系统 - 打包脚本
echo ================================================
echo.

echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/4] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [3/4] 安装开发依赖包（打包用）...
pip install pyinstaller
if errorlevel 1 (
    echo 警告: PyInstaller安装失败
)

echo.
echo [4/4] 开始打包...
pyinstaller LiteratureAgentSystem.spec --clean
if errorlevel 1 (
    echo 错误: 打包失败
    pause
    exit /b 1
)

echo.
echo ================================================
echo   打包完成！
echo ================================================
echo.
echo 可执行文件位置: dist\LiteratureAgentSystem\LiteratureAgentSystem.exe
echo.
echo 启动方式:
echo   1. 双击 LiteratureAgentSystem.exe 运行命令行版本
echo   2. 运行 api\app.py 启动Web服务
echo.
pause