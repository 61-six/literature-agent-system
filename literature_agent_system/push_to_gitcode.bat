@echo off
echo ================================================
echo   上传到 GitCode 仓库
echo ================================================
echo.
echo 请按照以下步骤操作：
echo.
echo [1] 在 GitCode 上创建新仓库
echo     访问：https://gitcode.net/new
echo     仓库名：literature-agent-system
echo.
echo [2] 配置 SSH 密钥（推荐）
echo     1. 生成密钥：ssh-keygen -t rsa -C "your@email.com"
echo     2. 复制公钥：cat ~/.ssh/id_rsa.pub
echo     3. 在 GitCode 设置中添加 SSH 密钥
echo.
echo [3] 关联远程仓库并推送
echo.
set /p repo_url="请输入 GitCode 仓库地址: "
echo.
echo 设置远程仓库...
git remote add gitcode %repo_url%
echo.
echo 推送代码...
git push -u gitcode main
echo.
echo 完成！
echo.
pause