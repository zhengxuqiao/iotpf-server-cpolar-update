#!/bin/bash

# extract-tunnel 服务安装脚本
# 此脚本安装 systemd 服务和定时器，用于自动从 cpolar access.log 中提取隧道信息并上传到 Git
#
# 作者：AI 助手生成
# 日期：2026-02-08

set -e

# 获取此脚本所在的目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 定义服务和定时器文件路径
SERVICE_FILE="$SCRIPT_DIR/extract-tunnel.service"
TIMER_FILE="$SCRIPT_DIR/extract-tunnel.timer"
SYSTEMD_DIR="/etc/systemd/system"

echo "正在安装 extract-tunnel 服务..."

# 检查是否以 root 用户运行
if [ "$EUID" -ne 0 ]; then
    echo "请以 root 用户运行或使用 sudo"
    exit 1
fi

# 复制服务和定时器文件到 systemd 目录
echo "正在将服务文件复制到 $SYSTEMD_DIR..."
cp "$SERVICE_FILE" "$SYSTEMD_DIR/"
cp "$TIMER_FILE" "$SYSTEMD_DIR/"

# 重载 systemd 守护进程以识别新的服务文件
echo "正在重载 systemd 守护进程..."
systemctl daemon-reload

# 启用并启动定时器
echo "正在启用并启动 extract-tunnel.timer..."
systemctl enable extract-tunnel.timer
systemctl start extract-tunnel.timer

# 显示定时器状态
echo ""
echo "安装成功完成！"
echo ""
echo "定时器状态:"
systemctl status extract-tunnel.timer --no-pager
echo ""
echo "查看日志，请使用:"
echo "  journalctl -u extract-tunnel.service -f"
echo ""
echo "停止定时器，请使用:"
echo "  systemctl stop extract-tunnel.timer"
echo ""
echo "禁用定时器开机自启，请使用:"
echo "  systemctl disable extract-tunnel.timer"
