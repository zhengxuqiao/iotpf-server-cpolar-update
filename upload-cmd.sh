#!/bin/bash

# tunnel.json 的 Git 上传脚本
# 此脚本添加所有更改，使用消息提交，并推送到 origin/master
# 由 extract-tunnel.py 在生成 tunnel.json 后调用

# 将所有更改添加到 Git
git add -A

# 使用通用消息提交更改
git commit -m "test"

# 将更改推送到 origin/master（强制覆盖远程）
git push -u origin master -f
