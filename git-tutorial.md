# Git 基础教程

## 什么是 Git

Git 是一个分布式版本控制系统，用于跟踪文件的变化历史，特别是在软件开发中协作和管理代码。

## Git 核心概念

- **Repository（仓库）**: 存储项目文件和历史记录的地方
- **Commit（提交）**: 保存文件更改的快照
- **Branch（分支）**: 代码的独立开发线
- **Master/Main**: 默认的主要分支
- **Remote（远程）**: 远程仓库的位置
- **Clone（克隆）**: 复制远程仓库到本地
- **Pull（拉取）**: 从远程仓库获取更新
- **Push（推送）**: 将本地更改上传到远程仓库

## 基本 Git 操作

### 1. 配置 Git
```bash
# 配置用户名
git config --global user.name "Your Name"

# 配置邮箱
git config --global user.email "you@example.com"
```

### 2. 初始化仓库
```bash
# 在项目目录中初始化新的 Git 仓库
git init
```

### 3. 检查状态
```bash
# 查看仓库当前状态
git status
```

### 4. 添加文件
```bash
# 添加单个文件
git add filename

# 添加所有更改的文件
git add .

# 添加特定类型的文件
git add *.txt
```

### 5. 提交更改
```bash
# 提交已添加的更改
git commit -m "提交信息说明"

# 提交并跳过暂存区
git commit -am "提交信息说明"
```

### 6. 查看历史
```bash
# 查看提交历史
git log

# 查看简洁的历史
git log --oneline

# 查看图形化历史
git log --graph --oneline --all
```

## 远程仓库操作

### 1. 添加远程仓库
```bash
# 添加远程仓库（通常命名为 origin）
git remote add origin https://github.com/username/repository.git
```

### 2. 推送到远程仓库
```bash
# 首次推送（设置上游分支）
git push -u origin main

# 后续推送
git push
```

### 3. 从远程仓库拉取
```bash
# 拉取远程更改
git pull

# 拉取特定分支
git pull origin main
```

### 4. 克隆远程仓库
```bash
# 克隆远程仓库到本地
git clone https://github.com/username/repository.git

# 克隆到指定目录
git clone https://github.com/username/repository.git directory-name
```

## 分支操作

### 1. 查看分支
```bash
# 查看本地分支
git branch

# 查看所有分支（包括远程）
git branch -a
```

### 2. 创建分支
```bash
# 创建新分支
git branch branch-name

# 创建并切换到新分支
git checkout -b branch-name

# Git 2.23+ 版本的新命令
git switch -c branch-name
```

### 3. 切换分支
```bash
# 切换分支
git checkout branch-name

# Git 2.23+ 版本的新命令
git switch branch-name
```

### 4. 合并分支
```bash
# 切换到目标分支，然后合并
git checkout main
git merge branch-name
```

### 5. 删除分支
```bash
# 删除本地分支
git branch -d branch-name

# 删除远程分支
git push origin --delete branch-name
```

## 常见 Git 命令

### 1. 查看差异
```bash
# 查看未暂存的更改
git diff

# 查看已暂存的更改
git diff --staged

# 查看特定文件的差异
git diff filename
```

### 2. 撤销操作
```bash
# 撤销工作目录中的更改
git checkout -- filename

# 撤销暂存
git reset HEAD filename

# 撤销最近一次提交（保留更改）
git reset --soft HEAD~1

# 撤销最近一次提交（丢弃更改）
git reset --hard HEAD~1
```

### 3. 暂存更改
```bash
# 暂存当前工作
git stash

# 恢复暂存的工作
git stash pop

# 查看暂存列表
git stash list
```

## .gitignore 文件

创建 `.gitignore` 文件来忽略不想跟踪的文件：

```
# 临时文件
*.tmp
*.temp

# 编译输出
*.o
*.exe
bin/

# 日志文件
*.log

# 依赖目录
node_modules/
vendor/

# 环境变量文件
.env
config.json
```

## 工作流程最佳实践

### 1. 标准开发流程
```bash
# 1. 获取最新的代码
git pull origin main

# 2. 创建功能分支
git checkout -b feature/new-feature

# 3. 开发并提交更改
git add .
git commit -m "Add new feature"

# 4. 推送到远程分支
git push origin feature/new-feature

# 5. 创建 Pull Request（在 GitHub 界面）

# 6. 合并后，切换回主分支
git checkout main

# 7. 获取合并后的最新代码
git pull origin main
```

### 2. 提交信息规范
- 使用祈使句（例如 "Add" 而不是 "Added"）
- 首字母大写
- 简洁明了
- 说明为什么和做什么，而不是怎么做

示例：
```
git commit -m "Add user authentication module"

git commit -m "Fix bug in payment processing"
```

## 常见问题解决

### 1. 解决合并冲突
当多人修改同一文件时，拉取代码可能会出现冲突：

```bash
# 1. 拉取时出现冲突
git pull origin main

# 2. 手动编辑冲突文件，解决冲突
# 冲突部分被标记为：
# <<<<<<< HEAD
# your changes
# =======
# incoming changes
# >>>>>>> branch-name

# 3. 添加解决后的文件
git add conflicted-file

# 4. 完成合并
git commit -m "Resolve merge conflict"
```

### 2. 连接到远程仓库失败
```bash
# 检查远程仓库URL
git remote -v

# 更改远程仓库URL
git remote set-url origin new-url

# 使用SSH代替HTTPS（如果已配置SSH密钥）
git remote set-url origin git@github.com:username/repository.git
```

### 3. 恢复误删文件
```bash
# 恢复特定文件到上一个版本
git checkout HEAD~1 -- filename

# 恢复所有未提交的更改
git checkout .
```

## GitHub 特殊操作

### 1. Fork 仓库
- 在 GitHub 网站上找到目标仓库
- 点击 "Fork" 按钮
- 克隆您 fork 的仓库
- 提交更改
- 创建 Pull Request

### 2. 同步 Fork 的仓库
```bash
# 添加上游仓库
git remote add upstream https://github.com/original-owner/original-repository.git

# 获取上游更改
git fetch upstream

# 合并上游更改
git checkout main
git merge upstream/main

# 推送到您的 Fork
git push origin main
```

这个教程涵盖了 Git 的基本使用方法，足以满足日常开发需求。随着经验增长，您可以探索更多高级功能。