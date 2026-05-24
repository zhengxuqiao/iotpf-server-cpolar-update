#!/bin/bash

# tunnel.json 的 Git 多仓库上传脚本
# 此脚本支持同时同步到 Gitee 和 GitHub 两个远程仓库
# 由 extract-tunnel.py 在生成 tunnel.json 后调用

# 定义远程仓库名称
GITEE_REMOTE="origin"
GITHUB_REMOTE="github"

# 将所有更改添加到 Git
echo "正在添加更改..."
git add -A

# 使用当前时间作为提交消息
COMMIT_MSG="Update tunnel.json - $(date '+%Y-%m-%d %H:%M:%S')"
echo "正在提交更改: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# 推送到 Gitee（默认远程仓库）
echo "正在推送到 Gitee..."
if git push -u $GITEE_REMOTE master -f; then
    echo "✓ Gitee 推送成功"
else
    echo "✗ Gitee 推送失败"
fi

# 推送到 GitHub（需要先配置 github 远程仓库）
echo "正在推送到 GitHub..."
if git push -u $GITHUB_REMOTE master -f; then
    echo "✓ GitHub 推送成功"
else
    echo "✗ GitHub 推送失败 - 请先配置 GitHub 远程仓库"
    echo "  使用以下命令配置: git remote add github https://github.com/your-username/your-repo.git"
fi

echo "上传完成！"