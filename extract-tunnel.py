#!/usr/bin/env python3
"""
extract-tunnel.py - 从 cpolar 的 access.log 中提取隧道信息并生成 tunnel.json

此脚本解析 cpolar 的 access.log 文件以提取隧道信息，
生成包含提取数据的 tunnel.json 文件，并运行 upload-cmd.sh 脚本
将更改上传到 Git 仓库。

作者：AI 助手生成
日期：2026-02-08
"""
import re
import json
import subprocess
from pathlib import Path

def extract_tunnel_info(log_file):
    """
    从 cpolar 的 access.log 文件中提取隧道信息。
    
    参数:
        log_file: access.log 文件的路径
    
    返回:
        以隧道名称为键、URL 为值的字典
    """
    tunnels = {}
    
    # 匹配包含隧道名称和 URL 的 NewTunnel 消息的模式
    # 日志文件在 JSON 中使用转义引号: \"TunnelName\":\"<name>\",\"Url\":\"<url>\"
    tunnel_name_pattern = re.compile(r'\\"TunnelName\\":\\"([^"]+)\\"[^}]*\\"Url\\":\\"([^"]+)\\"')
    
    # 读取整个日志文件
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 查找所有隧道名称和 URL 对
        matches = tunnel_name_pattern.finditer(content)
        
        for match in matches:
            tunnel_name = match.group(1)
            url = match.group(2)
            
            # 只为每个隧道名称保留最新的 URL
            tunnels[tunnel_name] = url
    
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
    # 根据要求仅过滤我们需要的隧道
    required_tunnels = {
        'cpolar-web': tunnels.get('cpolar-web', ''),
        'ssh': tunnels.get('ssh', ''),
        'thingsboard-mqtt': tunnels.get('thingsboard-mqtt', ''),
        'thingsboard-mqtt-ssl': tunnels.get('thingsboard-mqtt-ssl', ''),
        'thingsboard-web': tunnels.get('thingsboard-web', ''),
        'thingsboard-http-alt': tunnels.get('thingsboard-http-alt', '')
    }
    
    # 移除空条目
    required_tunnels = {k: v for k, v in required_tunnels.items() if v}
    
    # 将隧道信息写入 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(required_tunnels, f, indent=2, ensure_ascii=False)
    
    # 打印成功消息
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
        # 执行上传脚本
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
    # 定义相对于脚本位置的文件路径
    
    script_dir = Path(__file__).parent
    log_file = script_dir / 'access.log'
    output_file = script_dir / 'tunnel.json'
    upload_script = script_dir / 'upload-cmd.sh'
    
    # 检查日志文件是否存在
    if not log_file.exists():
        print(f"错误: 找不到日志文件 {log_file}")
        return 1
    
    # 提取隧道信息
    print("从 access.log 中提取隧道信息...")
    tunnels = extract_tunnel_info(log_file)
    
    if not tunnels:
        print("警告: 在日志文件中未找到隧道信息")
        return 1
    
    # 生成 tunnel.json
    print("\n正在生成 tunnel.json...")
    generate_tunnel_json(tunnels, output_file)
    
    # 运行上传脚本
    print("\n正在运行上传脚本...")
    run_upload_script(upload_script)
    
    print("\n完成！")
    return 0

if __name__ == '__main__':
    """
    脚本的入口点。
    """
    exit(main())
