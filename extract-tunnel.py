#!/usr/bin/env python3
import re
import json
import subprocess
from pathlib import Path

def extract_tunnel_info(log_file):
    """
    Extract tunnel information from cpolar access.log file.
    Returns a dictionary with tunnel names and their URLs.
    """
    tunnels = {}
    
    # Pattern to match NewTunnel messages with tunnel name and URL
    # The log file uses escaped quotes in JSON: \"TunnelName\":\"<name>\",\"Url\":\"<url>\"
    tunnel_name_pattern = re.compile(r'\\"TunnelName\\":\\"([^"]+)\\"[^}]*\\"Url\\":\\"([^"]+)\\"')
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Find all tunnel name and URL pairs
        matches = tunnel_name_pattern.finditer(content)
        
        for match in matches:
            tunnel_name = match.group(1)
            url = match.group(2)
            
            # Only keep the latest URL for each tunnel name
            tunnels[tunnel_name] = url
    
    return tunnels

def generate_tunnel_json(tunnels, output_file):
    """
    Generate tunnel.json file with the extracted tunnel information.
    """
    # Filter only the tunnels we need based on the requirements
    required_tunnels = {
        'cpolar-web': tunnels.get('cpolar-web', ''),
        'ssh': tunnels.get('ssh', ''),
        'thingsboard-mqtt': tunnels.get('thingsboard-mqtt', ''),
        'thingsboard-mqtt-ssl': tunnels.get('thingsboard-mqtt-ssl', ''),
        'thingsboard-web': tunnels.get('thingsboard-web', '')
    }
    
    # Remove empty entries
    required_tunnels = {k: v for k, v in required_tunnels.items() if v}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(required_tunnels, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {output_file} with {len(required_tunnels)} tunnels:")
    for name, url in required_tunnels.items():
        print(f"  {name}: {url}")
    
    return required_tunnels

def run_upload_script(script_path):
    """
    Run the upload-cmd.sh script to upload the tunnel.json file.
    """
    try:
        subprocess.run(['bash', script_path], check=True)
        print(f"Successfully executed {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_path}: {e}")
        raise

def main():
    # Define file paths
    script_dir = Path(__file__).parent
    log_file = script_dir / 'access.log'
    output_file = script_dir / 'tunnel.json'
    upload_script = script_dir / 'upload-cmd.sh'
    
    # Check if log file exists
    if not log_file.exists():
        print(f"Error: Log file {log_file} not found")
        return 1
    
    # Extract tunnel information
    print("Extracting tunnel information from access.log...")
    tunnels = extract_tunnel_info(log_file)
    
    if not tunnels:
        print("Warning: No tunnel information found in the log file")
        return 1
    
    # Generate tunnel.json
    print("\nGenerating tunnel.json...")
    generate_tunnel_json(tunnels, output_file)
    
    # Run upload script
    print("\nRunning upload script...")
    run_upload_script(upload_script)
    
    print("\nDone!")
    return 0

if __name__ == '__main__':
    exit(main())
