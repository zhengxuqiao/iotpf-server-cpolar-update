#!/usr/bin/env python3
"""
extract-tunnel.py - 从 cpolar 获取隧道信息并生成 tunnel.json

隧道信息源优先级：
  1. 本地 4040 接口（/api/tunnels，在线隧道最实时，不依赖日志级别/轮转）
  2. cpolar master 日志（NewTunnel/RespStartTunnel 消息，debug 级，含 TunnelName+Url）
  3. 旧 tunnel.json 兜底

生成 tunnel.json 后运行 upload-cmd.sh 推送到 Git 仓库。
"""
import re
import json
import subprocess
import urllib.request
from pathlib import Path

REQUIRED_TUNNEL_NAMES = [
    "ssh",
    "thingsboard-mqtt",
    "thingsboard-mqtts-token",
    "thingsboard-mqtts-cert",
    "thingsboard-web"
]


def get_tunnels_from_api():
    """从本地 4040 接口获取在线隧道信息（最实时）。"""
    try:
        with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=3) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        tunnels = {}
        for t in data.get("tunnels", []) or []:
            name = t.get("name") or t.get("TunnelName")
            url = t.get("public_url") or t.get("Url")
            if name and url:
                tunnels[name] = url
        return tunnels
    except Exception as e:
        print("本地 4040 接口获取失败: %r" % e)
        return {}


def extract_tunnel_info(log_files):
    """
    从 cpolar master 日志中提取隧道信息。

    参数:
        log_files: 日志文件路径列表（按最新优先排序）

    返回:
        以隧道名称为键、URL 为值的字典
    """
    tunnels = {}
    # 匹配包含隧道名称和 URL 的消息模式（NewTunnel/RespStartTunnel）
    # 日志文件在 JSON 中使用转义引号: \"TunnelName\":\"<name>\",\"Url\":\"<url>\"
    tunnel_name_pattern = re.compile(r'\\"TunnelName\\":\\"([^"]+)\\",\\"HostHeader\\":[^}]*\\"Url\\":\\"([^"]+)\\"')

    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            continue

        matches = list(tunnel_name_pattern.finditer(content))

        # 逆序遍历匹配项，找到每个隧道的第一个匹配项（该文件中最新的）
        for match in reversed(matches):
            tunnel_name = match.group(1)
            url = match.group(2)

            if tunnel_name in REQUIRED_TUNNEL_NAMES and tunnel_name not in tunnels:
                tunnels[tunnel_name] = url
                if len(tunnels) == len(REQUIRED_TUNNEL_NAMES):
                    return tunnels

    return tunnels


def generate_tunnel_json(tunnels, output_file):
    """
    生成包含提取的隧道信息的 tunnel.json 文件。

    参数:
        tunnels: 隧道名称和 URL 的字典
        output_file: 输出 JSON 文件的路径

    返回:
        包含所需隧道及其 URL 的字典
    """
    # 检查是否存在旧的 tunnel.json 文件
    old_tunnels = {}
    if output_file.exists():
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                old_tunnels = json.load(f)
        except json.JSONDecodeError:
            print(f"警告: 无法解析旧的 {output_file} 文件，将创建新文件")

    # 根据要求仅过滤我们需要的隧道，保留旧值
    required_tunnels = {}
    for tunnel_name in REQUIRED_TUNNEL_NAMES:
        if tunnel_name in tunnels:
            required_tunnels[tunnel_name] = tunnels[tunnel_name]
        elif tunnel_name in old_tunnels:
            required_tunnels[tunnel_name] = old_tunnels[tunnel_name]

    # 将隧道信息写入 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(required_tunnels, f, indent=2, ensure_ascii=False)

    print(f"已生成 {output_file}，包含 {len(required_tunnels)} 个隧道:")
    for name, url in required_tunnels.items():
        print(f"  {name}: {url}")

    return required_tunnels


def run_upload_script(script_path):
    """
    运行 upload-cmd.sh 脚本以上传 tunnel.json 文件。

    参数:
        script_path: upload-cmd.sh 脚本的路径

    异常:
        subprocess.CalledProcessError: 如果上传脚本失败
    """
    try:
        subprocess.run(['bash', script_path], check=True)
        print(f"成功执行 {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"执行 {script_path} 时出错: {e}")
        raise


def main():
    """
    协调整个隧道提取过程的主函数。

    返回:
        成功返回 0，失败返回 1
    """
    script_dir = Path(__file__).parent
    output_file = script_dir / 'tunnel.json'
    upload_script = script_dir / 'upload-cmd.sh'

    # 收集日志文件：隧道建立记录（NewTunnel/Tunnel established）在 worker 日志 access.log*，
    # master 日志 access.log.master.log* 作为补充。worker 优先、最新优先。
    log_dir = Path('/var/log/cpolar')
    worker_logs = sorted(log_dir.glob('access.log'), reverse=True) + \
                  sorted(log_dir.glob('access.log.202*'), reverse=True)
    master_logs = sorted(log_dir.glob('access.log.master.log*'), reverse=True)
    log_files = worker_logs + master_logs
    if not log_files:
        print("错误: 找不到任何 cpolar 日志文件 /var/log/cpolar/access.log*")
        return 1

    # 1) 先尝试本地 4040 接口（在线隧道最实时）
    print("从本地 4040 接口获取隧道信息...")
    tunnels = get_tunnels_from_api()
    source = "4040 接口"
    if not tunnels:
        # 2) 回退到日志解析（当天 + 历史）
        print("4040 接口无数据，从 master 日志提取隧道信息...")
        tunnels = extract_tunnel_info(log_files)
        source = "master 日志"

    if not tunnels:
        print(f"警告: {source} 中均未找到隧道信息（隧道当前离线，将沿用旧值）")

    # 生成 tunnel.json
    print("\n正在生成 tunnel.json...")
    generate_tunnel_json(tunnels, output_file)

    # 运行上传脚本
    print("\n正在运行上传脚本...")
    run_upload_script(upload_script)

    print("\n完成！")
    return 0


if __name__ == '__main__':
    exit(main())
