#!/usr/bin/env python3
# TeacherOS — Google Calendar 寫入腳本
# 用途：將行事曆事件直接寫入 Google Calendar（不只是更新本機 calendar.md）
#
# 前置條件（一次性設定）：
#   1. 至 Google Cloud Console 建立專案，啟用 Calendar API，下載 credentials.json
#   2. 將 credentials.json 放入 setup/ 資料夾（已列入 .gitignore）
#   3. 第一次執行時會開啟瀏覽器進行 OAuth 授權，之後自動使用 token.json
#
# 用法（AI 直接呼叫，不需教師手動輸入）：
#   python3 setup/gcal-write.py \
#     --title "春季班親會" \
#     --date "2026-03-21" \
#     --start "09:00" \
#     --end "11:00" \
#     --location "9C 教室" \
#     [--description "議程說明..."] \
#     [--calendar-id "primary"]

import argparse
import os
import sys
from datetime import datetime, date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SETUP_DIR = REPO_ROOT / "setup"
CREDENTIALS_FILE = SETUP_DIR / "credentials.json"
TOKEN_FILE = SETUP_DIR / "token.json"
ENV_FILE = SETUP_DIR / "environment.env"

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def load_env():
    """從 environment.env 讀取設定"""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip()
    return env


def get_credentials():
    """取得或更新 OAuth 憑證"""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None

    if not CREDENTIALS_FILE.exists():
        print("錯誤：找不到 setup/credentials.json")
        print("請依照設定說明從 Google Cloud Console 下載憑證檔案。")
        sys.exit(1)

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())

    return creds


def create_event(args, calendar_id):
    """在 Google Calendar 建立事件"""
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # 組合日期時間（台灣時區 UTC+8）
    start_dt = f"{args.date}T{args.start}:00+08:00"
    end_dt = f"{args.date}T{args.end}:00+08:00"

    event = {
        "summary": args.title,
        "location": args.location or "",
        "description": args.description or "",
        "start": {
            "dateTime": start_dt,
            "timeZone": "Asia/Taipei",
        },
        "end": {
            "dateTime": end_dt,
            "timeZone": "Asia/Taipei",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 60},
            ],
        },
    }

    created = service.events().insert(calendarId=calendar_id, body=event).execute()
    return created


def main():
    parser = argparse.ArgumentParser(description="TeacherOS：寫入 Google Calendar 行事曆")
    parser.add_argument("--title",       required=True,  help="事件標題")
    parser.add_argument("--date",        required=True,  help="日期（YYYY-MM-DD）")
    parser.add_argument("--start",       required=True,  help="開始時間（HH:MM）")
    parser.add_argument("--end",         required=True,  help="結束時間（HH:MM）")
    parser.add_argument("--location",    default="",     help="地點（選填）")
    parser.add_argument("--description", default="",     help="說明文字（選填）")
    parser.add_argument("--calendar-id", default=None,   help="日曆 ID（預設從 environment.env 讀取）")
    args = parser.parse_args()

    # 讀取 Calendar ID
    env = load_env()
    calendar_id = args.calendar_id or env.get("GCAL_CALENDAR_ID", "primary")

    print("")
    print("── TeacherOS Google Calendar 寫入 ─────────────")
    print(f"標題    ：{args.title}")
    print(f"日期    ：{args.date}  {args.start}–{args.end}")
    print(f"地點    ：{args.location or '（未填）'}")
    print(f"日曆 ID ：{calendar_id}")
    print("────────────────────────────────────────────────")

    try:
        event = create_event(args, calendar_id)
        print(f"完成。事件已寫入 Google Calendar。")
        print(f"事件連結：{event.get('htmlLink', '（無連結）')}")
        print("")
    except Exception as e:
        print(f"錯誤：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
