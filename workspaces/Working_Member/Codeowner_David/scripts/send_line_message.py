#!/usr/bin/env python3
"""
LINE 訊息發送腳本（文字 + 附檔）

用法：
  # 純文字（stdin）
  echo "訊息內容" | python3 send_line_message.py

  # 純文字（檔案）
  python3 send_line_message.py message.txt

  # 文字 + 附檔（附檔需提供公開 URL）
  echo "訊息內容" | python3 send_line_message.py --file-url "https://..." --file-name "檔案.pdf"

  # 文字 + 附檔（透過 gws 上傳到 Drive 取得公開連結）
  echo "訊息內容" | python3 send_line_message.py --upload "/path/to/file.pdf"
"""
import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path


def get_env_vars():
    """從 setup/environment.env 讀取環境變數"""
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


def upload_to_drive(file_path):
    """透過 gws CLI 上傳檔案到 Google Drive 並回傳公開連結"""
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: 找不到檔案 {file_path}")
        sys.exit(1)

    file_name = file_path.name

    # Step 1: 上傳到 Drive
    try:
        upload_result = subprocess.run(
            ["gws", "drive", "files", "create",
             "--upload", str(file_path)],
            capture_output=True, text=True, timeout=60
        )
        if upload_result.returncode != 0:
            print(f"ERROR: gws 上傳失敗 - {upload_result.stderr}")
            sys.exit(1)

        # 解析回傳的 file ID
        upload_data = json.loads(upload_result.stdout)
        file_id = upload_data.get("id")
        if not file_id:
            print(f"ERROR: 上傳成功但無法取得 file ID - {upload_result.stdout}")
            sys.exit(1)
    except FileNotFoundError:
        print("ERROR: gws CLI 未安裝。請先執行 gws setup。")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: gws 上傳逾時。")
        sys.exit(1)

    # Step 1.5: 重新命名檔案（gws create --upload 不支援同時設定檔名）
    try:
        rename_result = subprocess.run(
            ["gws", "drive", "files", "update",
             "--params", json.dumps({"fileId": file_id}),
             "--json", json.dumps({"name": file_name})],
            capture_output=True, text=True, timeout=30
        )
        if rename_result.returncode != 0:
            # 重新命名失敗不致命，繼續使用原始檔名
            pass
    except (subprocess.TimeoutExpired, Exception):
        pass

    # Step 2: 設定公開權限（anyone with link can view）
    try:
        perm_result = subprocess.run(
            ["gws", "drive", "permissions", "create",
             "--params", json.dumps({"fileId": file_id}),
             "--json", json.dumps({"role": "reader", "type": "anyone"})],
            capture_output=True, text=True, timeout=30
        )
        if perm_result.returncode != 0:
            print(f"ERROR: 設定權限失敗 - {perm_result.stderr}")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: 設定權限逾時。")
        sys.exit(1)

    # Step 3: 組合連結
    # HTML 檔案透過 Apps Script 瀏覽器渲染，其他檔案用 Drive 直接連結
    if file_name.lower().endswith(".html"):
        apps_script_url = "https://script.google.com/macros/s/AKfycbzP1ccndlHppGo35kXqcLTVUlhzVrjvi5N63fhKZeh18SY30Yn8EJgzth-N2lKT9-tegg/exec"
        view_url = f"{apps_script_url}?id={file_id}"
    else:
        view_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    return view_url, file_name


def send_push(token, group_id, messages):
    """呼叫 LINE Push API 發送訊息"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "to": group_id,
        "messages": messages
    }

    req = urllib.request.Request(
        url, data=json.dumps(data).encode("utf-8"),
        headers=headers, method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            response.read().decode("utf-8")
            if response.status == 200:
                return True
            else:
                print(f"FAILED: HTTP {response.status}")
                return False
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"ERROR: API 呼叫失敗 - HTTP {e.code} - {err_body}")
        return False
    except Exception as e:
        print(f"ERROR: 未預期錯誤 - {str(e)}")
        return False


def build_file_flex_message(file_url, file_name):
    """建立 Flex Message 卡片，讓家長點擊下載檔案"""
    return {
        "type": "flex",
        "altText": f"附檔：{file_name}",
        "contents": {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "📎",
                                "size": "xl",
                                "align": "center"
                            }
                        ],
                        "width": "40px",
                        "justifyContent": "center"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": file_name,
                                "weight": "bold",
                                "size": "sm",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": "點擊下方按鈕開啟檔案",
                                "size": "xs",
                                "color": "#999999",
                                "margin": "sm"
                            }
                        ],
                        "flex": 1
                    }
                ],
                "paddingAll": "lg"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "開啟檔案",
                            "uri": file_url
                        },
                        "style": "primary",
                        "color": "#06C755",
                        "height": "sm"
                    }
                ],
                "paddingAll": "md"
            }
        }
    }


def parse_args(argv):
    """簡易參數解析"""
    args = {
        "text_source": None,  # 檔案路徑或 None（用 stdin）
        "file_url": None,
        "file_name": None,
        "upload": None,
    }

    i = 1
    while i < len(argv):
        if argv[i] == "--file-url" and i + 1 < len(argv):
            args["file_url"] = argv[i + 1]
            i += 2
        elif argv[i] == "--file-name" and i + 1 < len(argv):
            args["file_name"] = argv[i + 1]
            i += 2
        elif argv[i] == "--upload" and i + 1 < len(argv):
            args["upload"] = argv[i + 1]
            i += 2
        elif not argv[i].startswith("--"):
            args["text_source"] = argv[i]
            i += 1
        else:
            i += 1

    return args


if __name__ == "__main__":
    args = parse_args(sys.argv)

    # 讀取文字內容
    message = ""
    if args["text_source"]:
        try:
            with open(args["text_source"], "r", encoding="utf-8") as f:
                message = f.read().strip()
        except Exception as e:
            print(f"ERROR: 無法讀取檔案 {args['text_source']} - {str(e)}")
            sys.exit(1)
    else:
        if not sys.stdin.isatty():
            message = sys.stdin.read().strip()

    # 取得 LINE 憑證
    envs = get_env_vars()
    token = envs.get("LINE_CHANNEL_ACCESS_TOKEN") or os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    group_id = envs.get("LINE_PARENT_GROUP_ID") or os.environ.get("LINE_PARENT_GROUP_ID")

    if not token or not group_id:
        print("ERROR: LINE_CHANNEL_ACCESS_TOKEN 或 LINE_PARENT_GROUP_ID 未設定。請確認 setup/environment.env。")
        sys.exit(1)

    if token.startswith("你的") or group_id.startswith("你的"):
        print("ERROR: LINE 憑證未填寫真實數值，請修改 setup/environment.env。")
        sys.exit(1)

    # 處理附檔
    file_url = args["file_url"]
    file_name = args["file_name"]

    if args["upload"]:
        # 透過 gws 上傳到 Drive
        file_url, auto_name = upload_to_drive(args["upload"])
        if not file_name:
            file_name = auto_name

    # 組合訊息
    messages = []

    if message:
        messages.append({"type": "text", "text": message})

    if file_url:
        if not file_name:
            file_name = "附檔"
        messages.append(build_file_flex_message(file_url, file_name))

    if not messages:
        print("ERROR: 沒有文字也沒有附檔，無法發送空訊息。")
        sys.exit(1)

    # 發送
    if send_push(token, group_id, messages):
        parts = []
        if message:
            parts.append("文字訊息")
        if file_url:
            parts.append(f"附檔卡片（{file_name}）")
        print(f"SUCCESS: LINE 發送成功 — {' + '.join(parts)}。")
    else:
        sys.exit(1)
