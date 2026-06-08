@echo off
echo ================================================
echo   GitHub上传到GitHub仓库
echo ================================================
echo.
echo 请按照以下步骤操作：
echo.
echo [1] 在 GitHub 上创建新仓库
echo     访问：https://github.com/new
echo.
echo [2] 将本地仓库关联到 GitHub
echo.
set /p repo_url="请输入GitHub仓库地址 (例如: https://github.com/your-username/literature-agent-system.git): "
echo.
echo 正在设置远程仓库...
cd literature_agent_system
git remote add origin %repo_url%
git branch -M main
echo.
echo 正在推送到GitHub...
git push -u origin main
echo.
echo 完成！
echo.
echo 访问您的仓库：%repo_url%
echo.
pause