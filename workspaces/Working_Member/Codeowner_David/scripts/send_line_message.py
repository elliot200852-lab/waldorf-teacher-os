#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

def get_env_vars():
    # Read from setup/environment.env
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    env_path = repo_root / "setup" / "environment.env"
    
    envs = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, val = line.split("=", 1)
                        envs[key.strip()] = val.strip()
    return envs

def send_line_message(message):
    envs = get_env_vars()
    
    token = envs.get("LINE_CHANNEL_ACCESS_TOKEN") or os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    group_id = envs.get("LINE_PARENT_GROUP_ID") or os.environ.get("LINE_PARENT_GROUP_ID")
    
    if not token or not group_id:
        print("ERROR: LINE_CHANNEL_ACCESS_TOKEN 或 LINE_PARENT_GROUP_ID 未設定。請確認 setup/environment.env。")
        sys.exit(1)
        
    if token.startswith("你的") or group_id.startswith("你的"):
        print("ERROR: LINE 憑證未填寫真實數值，請修改 setup/environment.env。")
        sys.exit(1)

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "to": group_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            if response.status == 200:
                print("SUCCESS: LINE 訊息發送成功。")
            else:
                print(f"FAILED: HTTP {response.status} - {res_body}")
                sys.exit(1)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"ERROR: 呼叫 API 失敗 - HTTP {e.code} - {err_body}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: 發生未預期錯誤 - {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    message = ""
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                message = f.read()
        except Exception as e:
            print(f"ERROR: 無法讀取檔案 {filepath} - {str(e)}")
            sys.exit(1)
    else:
        message = sys.stdin.read()
        
    if not message.strip():
        print("ERROR: 要發送的訊息不可為空。")
        sys.exit(1)
        
    send_line_message(message.strip())
