# GitCode 上传指南
=================

## 快速开始

### 第一步：创建 GitCode 仓库

1. 访问：https://gitcode.net/new

2. 填写仓库信息：
   - 仓库名称：`literature-agent-system`
   - 可见性：公开 公开或私有
   - 不要勾选：
     - 添加 .gitignore
     - 添加 LICENSE
     - 添加 README.md

3. 点击"创建仓库"

### 第二步：创建个人访问令牌

1. 访问：https://gitcode.net/-/profile/personal_access_tokens

2. 点击"创建新的个人访问令牌"

3. 填写信息：
   - 名称：`Push Token`（或其他名称）
   - 过期时间：选择 365天（或其他
   - 勾选权限：
     - `write_repository`（必须勾选

4. 点击"创建个人访问令牌"

5. ⚠️ **重要**：复制生成的令牌（只显示一次！）

### 第三步：推送代码

#### 方法一：使用脚本（推荐）

双击运行：`push_to_gitcode.bat`

#### 方法二：手动推送

```bash
cd literature_agent_system
git push -u gitcode main
```

首次推送时会提示输入凭证：
- 用户名：您的GitCode用户名（如：61-six）
- 密码：刚才创建的个人访问令牌

## 远程仓库配置

当前已配置的远程仓库：

```bash
# 查看远程仓库
git remote -v
```

输出示例：
```
gitcode  https://gitcode.net/61-six/literature-agent-system.git (fetch)
gitcode  https://gitcode.net/61-six/literature-agent-system.git (push)
origin   https://github.com/61-six/literature-agent-system.git (fetch)
origin   https://github.com/61-six/literature-agent-system.git (push)
```

## 常用命令

```bash
# 查看远程仓库
git remote -v

# 推送到 GitHub
git push origin main

# 推送到 GitCode
git push gitcode main

# 同时推送到两个仓库
git push origin main ; git push gitcode main
```

## 常见问题

### 1. 认证失败

如果遇到认证失败：

1. 确保个人访问令牌是否正确
2. 确保令牌有 `write_repository` 权限
3. 清除旧凭据：
   ```bash
   git config --global --unset credential.helper
   ```

### 2. 仓库不存在

确保在 GitCode 上先创建了仓库

### 3. 网络问题

如果遇到网络问题，可以尝试：
- 检查网络连接
- 尝试使用 SSH 方式（需要配置 SSH 密钥）

## 访问地址

- GitHub: https://github.com/61-six/literature-agent-system
- GitCode: https://gitcode.net/61-six/literature-agent-system

## 下一步

上传成功后，您可以：

1. 在 GitCode 上查看项目
2. 创建 README.md
3. 设置项目描述
4. 添加开源许可证
