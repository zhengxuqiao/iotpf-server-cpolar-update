# iotpf-server-cpolar-update

## 介绍
本项目用于从 cpolar 的 access.log 日志文件中自动提取隧道信息，生成 tunnel.json 文件，并通过 upload-cmd.sh 脚本自动上传到远程仓库。

## 功能特性
- 自动从 cpolar access.log 中提取隧道信息
- 生成标准化的 tunnel.json 文件
- 自动上传到 Git 仓库
- 支持定时任务，每分钟自动执行一次

## 提取的隧道信息
系统会从 access.log 中提取以下隧道信息并记录到 tunnel.json 文件：
- cpolar-web: http://314f08e7.r29.cpolar.top
- ssh: tcp://29.tcp.cpolar.top:10976
- thingsboard-mqtt: tcp://29.tcp.cpolar.top:12019
- thingsboard-mqtt-ssl: tcp://29.tcp.cpolar.top:10537
- thingsboard-web: http://4d25139f.r29.cpolar.top

## 软件架构
- extract-tunnel.py: Python 脚本，负责解析 access.log 并提取隧道信息
- extract-tunnel.service: systemd 服务文件
- extract-tunnel.timer: systemd 定时器，每分钟执行一次
- install.sh: 安装脚本
- upload-cmd.sh: Git 上传脚本

## 安装教程

### 前置要求
- Linux 系统（支持 systemd）
- Python 3
- Git 配置完成
- cpolar 运行并生成 access.log

### 安装步骤

1. 克隆或下载本项目到服务器

2. 确保文件权限正确：
```bash
chmod +x extract-tunnel.py
chmod +x install.sh
chmod +x upload-cmd.sh
```

3. 运行安装脚本（需要 root 权限）：
```bash
sudo ./install.sh
```

安装脚本会自动完成以下操作：
- 复制服务和定时器文件到 /etc/systemd/system/
- 重载 systemd 守护进程
- 启用并启动定时器

## 使用说明

### 手动执行
如果需要手动执行提取脚本：
```bash
python3 extract-tunnel.py
```

### 查看服务状态
查看定时器状态：
```bash
systemctl status extract-tunnel.timer
```

查看服务执行日志：
```bash
journalctl -u extract-tunnel.service -f
```

### 停止定时任务
停止定时器：
```bash
systemctl stop extract-tunnel.timer
```

禁用开机自启：
```bash
systemctl disable extract-tunnel.timer
```

### 重新启动定时任务
```bash
systemctl start extract-tunnel.timer
```

## 文件说明

### extract-tunnel.py
主程序脚本，功能包括：
- 读取 access.log 文件
- 使用正则表达式提取隧道名称和 URL
- 生成 tunnel.json 文件
- 调用 upload-cmd.sh 上传文件

### tunnel.json
生成的 JSON 文件，包含当前所有活跃的隧道信息，格式如下：
```json
{
  "cpolar-web": "http://314f08e7.r29.cpolar.top",
  "ssh": "tcp://29.tcp.cpolar.top:10976",
  "thingsboard-mqtt": "tcp://29.tcp.cpolar.top:12019",
  "thingsboard-mqtt-ssl": "tcp://29.tcp.cpolar.top:10537",
  "thingsboard-web": "http://4d25139f.r29.cpolar.top"
}
```

### upload-cmd.sh
Git 上传脚本，将生成的 tunnel.json 提交并推送到远程仓库。

## 故障排除

### 脚本执行失败
检查 Python 是否正确安装：
```bash
python3 --version
```

检查 access.log 文件是否存在：
```bash
ls -l access.log
```

查看详细错误日志：
```bash
journalctl -u extract-tunnel.service -n 50
```

### Git 上传失败
检查 Git 配置：
```bash
git config --list
```

检查远程仓库连接：
```bash
git remote -v
```

手动测试上传脚本：
```bash
bash upload-cmd.sh
```

### 定时器未运行
检查定时器状态：
```bash
systemctl list-timers | grep extract-tunnel
```

如果定时器未运行，重新启动：
```bash
systemctl restart extract-tunnel.timer
```

## 卸载

如需卸载服务：
```bash
sudo systemctl stop extract-tunnel.timer
sudo systemctl disable extract-tunnel.timer
sudo rm /etc/systemd/system/extract-tunnel.service
sudo rm /etc/systemd/system/extract-tunnel.timer
sudo systemctl daemon-reload
```

## 参与贡献

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request

## 许可证
本项目采用 MIT 许可证

