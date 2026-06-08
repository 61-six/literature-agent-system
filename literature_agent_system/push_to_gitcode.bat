@echo off
chcp 65001 >nul
echo ================================================
echo   上传到 GitCode 仓库
echo ================================================
echo.
echo 请先完成以下步骤：
echo.
echo [1] 在 GitCode 上创建仓库
echo     访问：https://gitcode.net/new
echo     仓库名：literature-agent-system
echo     选择：公开或私有
echo     不要勾选 "添加 .gitignore"、"添加 LICENSE"、"添加 README"
echo.
echo [2] 获取访问令牌
echo     访问：https://gitcode.net/-/profile/personal_access_tokens
echo     点击 "创建新的个人访问令牌"
echo     输入名称：例如 "Push Token"
echo     选择过期时间：例如 "365天"
echo     勾选权限：write_repository
echo     点击 "创建个人访问令牌"
echo     复制生成的令牌（只显示一次）
echo.
echo [3] 配置 Git 凭证
echo     首次推送时，使用以下凭证：
echo     用户名：您的GitCode用户名（如：61-six）
echo     密码：刚才创建的个人访问令牌
echo.
echo ================================================
echo.
set /p confirm="已经准备好了吗？(y/n): "
if /i not "%confirm%"=="y" (
    echo 请先完成上述步骤，然后再运行此脚本。
    pause
    exit /b
)

echo.
echo 正在推送到 GitCode...
git push -u gitcode main

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo   上传成功！
    echo ================================================
    echo.
    echo 访问您的仓库：https://gitcode.net/61-six/literature-agent-system
    echo.
) else (
    echo.
    echo ================================================
    echo   上传失败！
    echo ================================================
    echo.
    echo 可能的原因：
    echo 1. 仓库还未在 GitCode 创建
    echo 2. 凭证认证失败
    echo 3. 网络连接问题
    echo.
    echo 请检查后重试。
    echo.
)
pause
