#!/usr/bin/env python3
# TeacherOS - 新增教師工作空間（管理員工具）
# 路徑：setup/add-teacher.py
# 用途：David（管理員）為新教師建立 workspace 與權限
# 使用方式：
#   python3 setup/add-teacher.py --name "陳佩珊" --email "vernachen327@gmail.com" --github "vernachen327"
#   python3 setup/add-teacher.py                    （互動模式）
#   python3 setup/add-teacher.py --dry-run --name …  （預覽模式，不實際執行）

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# 終端顏色與符號
# ============================================================

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"

CHECK = "v"
WARN = "!"
ERROR = "x"
INFO = "i"


def print_banner():
    print()
    print(f"{BLUE}{'='*55}{NC}")
    print(f"{BLUE}  TeacherOS - 新增教師工作空間{NC}")
    print(f"{BLUE}  管理員工具（僅限 David）{NC}")
    print(f"{BLUE}{'='*55}{NC}")
    print()


def print_section(msg):
    print()
    print(f"{BLUE}{'─'*55}{NC}")
    print(f"{BLUE}{msg}{NC}")
    print(f"{BLUE}{'─'*55}{NC}")


def print_success(msg):
    print(f"{GREEN}{CHECK} {msg}{NC}")


def print_warning(msg):
    print(f"{YELLOW}{WARN} {msg}{NC}")


def print_error(msg):
    print(f"{RED}{ERROR} {msg}{NC}")


def print_info(msg):
    print(f"{BLUE}{INFO} {msg}{NC}")


# ============================================================
# 互動輸入工具
# ============================================================

def get_input(prompt_msg: str) -> str:
    """必填欄位：反覆詢問直到非空。"""
    while True:
        value = input(f"{CYAN}{prompt_msg}{NC}: ").strip()
        if value:
            return value
        print_error("此欄位不可為空")


def get_optional_input(prompt_msg: str, default: str = "") -> str:
    """選填欄位：可直接 Enter 跳過。"""
    if default:
        suffix = f" (預設: {default})"
    else:
        suffix = " (選填，按 Enter 跳過)"
    value = input(f"{CYAN}{prompt_msg}{suffix}{NC}: ").strip()
    return value if value else default


# ============================================================
# 核心邏輯
# ============================================================

class AddTeacher:
    def __init__(self, *, name: str, email: str, github: str,
                 class_code: str = "", subject: str = "",
                 teacher_id: str = "", dry_run: bool = False):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.name = name
        self.email = email
        self.github = github
        self.class_code = class_code
        self.subject = subject
        self.teacher_id = teacher_id or f"Teacher_{name}"
        self.dry_run = dry_run

        self.workspace_dir = self.repo_root / "workspaces" / "Working_Member" / self.teacher_id
        self.template_dir = self.repo_root / "workspaces" / "_template"
        self.acl_file = self.repo_root / "ai-core" / "acl.yaml"
        self.branch_name = f"workspace/{self.teacher_id}"
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        self.date_today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # ── Step 1: 管理員確認 ──

    def check_admin(self):
        if not self.acl_file.exists():
            print_error(f"找不到 {self.acl_file}")
            sys.exit(1)
        print_info("確認管理員身份...")
        print_warning("此腳本僅限 David（管理員）使用")
        print()
        confirm = input(f"{YELLOW}確認你是管理員？(yes/no): {NC}").strip()
        if confirm != "yes":
            print_error("操作取消。此腳本僅供管理員使用。")
            sys.exit(1)
        print()

    # ── Step 2: 確認資訊 ──

    def confirm_info(self):
        print_section("確認教師資訊")
        print()
        print(f"{CYAN}即將建立以下工作空間：{NC}")
        print()
        print(f"  教師姓名：    {self.name}")
        print(f"  Email：       {self.email}")
        print(f"  GitHub 帳號： {self.github}")
        if self.class_code:
            print(f"  班級代碼：    {self.class_code}")
        else:
            print(f"  班級代碼：    （未指定，教師可稍後建立）")
        if self.subject:
            print(f"  主要科目：    {self.subject}")
        else:
            print(f"  主要科目：    （未指定，教師可稍後建立）")
        print(f"  Workspace ID：{self.teacher_id}")

        if self.dry_run:
            print()
            print(f"{YELLOW}[預覽模式] 以下為模擬執行，不會實際建立任何檔案。{NC}")
        print()

        confirm = input(f"{YELLOW}以上資訊正確？(yes/no): {NC}").strip()
        if confirm != "yes":
            print_error("操作取消")
            sys.exit(1)
        print()

    # ── Step 3: 建立 workspace ──

    def create_workspace(self):
        print_section("步驟 1：建立 workspace 目錄")

        if self.workspace_dir.exists():
            print_error(f"工作空間目錄已存在：{self.workspace_dir}")
            sys.exit(1)

        if self.dry_run:
            print_info(f"[預覽] 將建立目錄：{self.workspace_dir}")
            print_info("[預覽] 將複製模板檔案")
            print_info("[預覽] 將建立 skills/ 目錄")
            return

        # 建立主目錄
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"目錄已建立：{self.workspace_dir}")

        # 複製 teacheros-personal.yaml
        src_personal = self.template_dir / "teacheros-personal.yaml"
        if src_personal.exists():
            dst_personal = self.workspace_dir / "teacheros-personal.yaml"
            shutil.copy2(src_personal, dst_personal)
            # 替換 {USER_EMAIL} 佔位符
            content = dst_personal.read_text(encoding="utf-8")
            content = content.replace("{USER_EMAIL}", self.email)
            dst_personal.write_text(content, encoding="utf-8")
            print_success(f"teacheros-personal.yaml 已複製，google_accounts 已填入 {self.email}")
        else:
            print_warning("teacheros-personal.yaml 模板不存在 — 教師須自行建立")

        # 複製 README.md
        src_readme = self.template_dir / "README.md"
        if src_readme.exists():
            shutil.copy2(src_readme, self.workspace_dir / "README.md")
            print_success("README.md 已複製")

        # 建立 skills 目錄與其中的檔案
        skills_dir = self.workspace_dir / "skills"
        src_skills = self.template_dir / "skills"
        if src_skills.exists() and src_skills.is_dir():
            shutil.copytree(src_skills, skills_dir)
            print_success("skills/ 目錄已複製")
        else:
            skills_dir.mkdir(parents=True, exist_ok=True)
            print_success("skills/ 目錄已建立")

        # 建立 workspace.yaml
        self._create_workspace_yaml()

    def _create_workspace_yaml(self):
        print_info("建立 workspace.yaml...")

        class_code_val = self.class_code if self.class_code else "(not yet assigned)"
        subject_val = self.subject if self.subject else "(not yet assigned)"

        content = f"""\
# TeacherOS - Teacher Workspace Configuration
# Path: workspaces/Working_Member/{self.teacher_id}/workspace.yaml

teacher:
  name: {self.name}
  email: {self.email}
  github_username: {self.github}
  teacher_id: {self.teacher_id}

teaching:
  class_code: {class_code_val}
  primary_subject: {subject_val}

workspace:
  path: workspaces/Working_Member/{self.teacher_id}/
  created_at: {self.timestamp}
  status: active
"""
        ws_yaml = self.workspace_dir / "workspace.yaml"
        ws_yaml.write_text(content, encoding="utf-8")
        print_success("workspace.yaml 已建立")

    # ── Step 4: 建立 env-preset.env ──

    def create_env_preset(self):
        print_section("步驟 2：建立 env-preset.env")

        if self.dry_run:
            print_info("[預覽] 將建立 env-preset.env")
            return

        content = f"""\
# TeacherOS — 個人環境預設檔（管理員自動產生）
# ─────────────────────────────────────────────────────────────
# 此檔案由 add-teacher 流程自動建立，包含已知的必填欄位。
# 執行 bash setup/start.sh（或 .\setup\start.ps1）時，系統會自動偵測並複製為
# setup/environment.env，你不需要手動編輯必填欄位。
#
# 選填欄位（Google Drive、Pandoc 等）請在 setup/environment.env
# 建立後，依需求自行補充。

# ── 必填（已由管理員預填）────────────────────────────────────

USER_NAME={self.name}
USER_EMAIL={self.email}
WORKSPACE_ID={self.teacher_id}
GITHUB_USERNAME={self.github}

# ── 選填（依需求自行補充至 setup/environment.env）──────────

# GOOGLE_DRIVE_EMAIL=你的帳號@gmail.com
# GOOGLE_DRIVE_FOLDER=00-01-TeacherOS-專案三層記憶
# PANDOC_PATH=/opt/homebrew/bin/pandoc
# GCAL_CALENDAR_ID=primary
# GWS_SERVICES=drive,calendar
"""
        env_file = self.workspace_dir / "env-preset.env"
        env_file.write_text(content, encoding="utf-8")
        print_success("env-preset.env 已建立")

    # ── Step 5: 更新 acl.yaml ──

    def update_acl(self):
        print_section("步驟 3：更新權限（acl.yaml）")

        if not self.acl_file.exists():
            print_error("ai-core/acl.yaml 不存在")
            sys.exit(1)

        new_entry_lines = [
            f"    - name: {self.name}",
            f"      email: {self.email}",
            f"      github_username: {self.github}",
            f"      workspace: workspaces/Working_Member/{self.teacher_id}/",
            f"      allowed_paths:",
            f"        - workspaces/Working_Member/{self.teacher_id}/",
            f"      blocked_paths:",
            f"        - ai-core/",
            f"        - setup/",
            f"        - .github/",
            f"        - publish/build.sh",
        ]
        new_entry = "\n".join(new_entry_lines)

        acl_content = self.acl_file.read_text(encoding="utf-8")

        # 檢查是否已存在同名教師
        if re.search(rf"^\s+- name: {re.escape(self.name)}\s*$", acl_content, re.MULTILINE):
            print_warning(f"acl.yaml 中已存在 '{self.name}' 的條目，跳過新增")
            return

        # 策略：找到最後一個 teacher 條目的 blocked_paths 區塊結尾
        # （即 publish/build.sh 那一行之後），在那裡插入新條目。
        # 這樣新條目會加在教師清單的最後面。

        # 找到 "  teachers:" 之後的所有教師條目
        # 我們要在 protected_always: 之前插入
        pattern = r"(^protected_always:)"
        match = re.search(pattern, acl_content, re.MULTILINE)

        if match:
            insert_pos = match.start()
            # 確保新條目前後有空行
            before = acl_content[:insert_pos].rstrip("\n")
            after = acl_content[insert_pos:]

            updated_content = before + "\n\n" + new_entry + "\n\n" + after
        else:
            # 備案：如果找不到 protected_always，附加在檔案末尾
            print_warning("找不到 protected_always 區塊，將條目附加在檔案末尾")
            updated_content = acl_content.rstrip("\n") + "\n\n" + new_entry + "\n"

        if self.dry_run:
            print_info("[預覽] 將在 acl.yaml 中新增以下條目：")
            print()
            for line in new_entry_lines:
                print(f"  {line}")
            print()
            return

        self.acl_file.write_text(updated_content, encoding="utf-8")
        print_success("acl.yaml 已更新")

    # ── Step 6: 建立班級資料夾 ──

    def create_class_folder(self):
        if not self.class_code:
            print_section("步驟 4：建立班級資料夾 — 跳過（未指定班級代碼）")
            print_info("教師可稍後在自己的 workspace 中建立班級資料夾。")
            return

        print_section("步驟 4：建立班級資料夾")

        class_dir = self.workspace_dir / "projects" / f"class-{self.class_code}"

        if self.dry_run:
            print_info(f"[預覽] 將建立班級資料夾：projects/class-{self.class_code}/")
            print_info(f"[預覽] 將建立 project.yaml")
            return

        class_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"班級資料夾已建立：projects/class-{self.class_code}/")

        project_yaml = class_dir / "project.yaml"
        if not project_yaml.exists():
            content = f"""\
# TeacherOS - Class Project Configuration
# Path: workspaces/{self.teacher_id}/projects/class-{self.class_code}/project.yaml

class:
  code: {self.class_code}
  subject: {self.subject if self.subject else "(not yet assigned)"}
  teacher_id: {self.teacher_id}

status:
  created_at: {self.date_today}
  last_updated: {self.date_today}
"""
            project_yaml.write_text(content, encoding="utf-8")
            print_success("project.yaml 已建立")

    # ── Step 7: 建立教師分支 ──

    def create_teacher_branch(self):
        print_section("步驟 5：建立教師分支")

        print_info(f"建立分支：{self.branch_name}")

        if self.dry_run:
            print_info(f"[預覽] 將建立 git 分支：{self.branch_name}")
            print_info(f"[預覽] 將推送至 origin")
            return

        try:
            subprocess.run(
                ["git", "checkout", "-b", self.branch_name],
                cwd=str(self.repo_root), check=True,
                capture_output=True, text=True,
            )
            subprocess.run(
                ["git", "push", "-u", "origin", self.branch_name],
                cwd=str(self.repo_root), check=True,
                capture_output=True, text=True,
            )
            subprocess.run(
                ["git", "checkout", "main"],
                cwd=str(self.repo_root), check=True,
                capture_output=True, text=True,
            )
            print_success(f"分支 '{self.branch_name}' 已建立並推送至 GitHub")
        except subprocess.CalledProcessError as e:
            print_error(f"Git 操作失敗：{e.stderr.strip()}")
            print_warning("請手動建立分支，或確認 git 狀態後重試。")

    # ── Step 8: 結果報告 ──

    def print_summary(self):
        print_section("步驟 6：設定完成")

        mode_label = " [預覽模式]" if self.dry_run else ""
        print()
        print(f"{GREEN}{'='*55}{NC}")
        print(f"{GREEN}  教師工作空間建立完成！{mode_label}{NC}")
        print(f"{GREEN}{'='*55}{NC}")
        print()

        print(f"{CYAN}已建立的資源：{NC}")
        print(f"  {CHECK} Workspace 目錄：workspaces/Working_Member/{self.teacher_id}/")
        if self.class_code:
            print(f"  {CHECK} 班級資料夾：workspaces/Working_Member/{self.teacher_id}/projects/class-{self.class_code}/")
        print(f"  {CHECK} 權限已更新：ai-core/acl.yaml")
        print(f"  {CHECK} 教師分支：{self.branch_name}")
        print()

        # 自我檢查清單
        print(f"{YELLOW}{'='*55}{NC}")
        print(f"{YELLOW}  自我檢查（David 通知教師前請確認）{NC}")
        print(f"{YELLOW}{'='*55}{NC}")
        print()
        print(f"  [ ] acl.yaml 中的 email 與教師的 environment.env 一致")
        print(f"      已註冊 email：{self.email}")
        print()
        print(f"  [ ] acl.yaml 中的 github_username 正確")
        print(f"      已註冊帳號：{self.github}")
        print()
        print(f"  [ ] 已 commit 並 push，教師可以 pull")
        print()

        print(f"{CYAN}請傳送以下資訊給新教師：{NC}")
        print()
        print(f"  - 確認 email：{self.email}")
        print(f"    （必須與你的 setup/environment.env 中的 USER_EMAIL 一致）")
        print(f"  - 個人分支：{self.branch_name}")
        print(f"  - 執行：bash setup/start.sh（Mac/Linux）或 .\\setup\\start.ps1（Windows）")
        print()

        print_info(f"設定全部完成。歡迎 {self.name} 加入 TeacherOS！")
        print()

    # ── 主流程 ──

    def run(self):
        print_banner()
        self.check_admin()
        self.confirm_info()
        self.create_workspace()
        self.create_env_preset()
        self.update_acl()
        self.create_class_folder()
        self.create_teacher_branch()
        self.print_summary()


# ============================================================
# 進入點
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="TeacherOS — 新增教師工作空間（管理員工具）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
範例：
  # 命令列模式（必填參數）
  python3 setup/add-teacher.py --name "陳佩珊" --email "vernachen327@gmail.com" --github "vernachen327"

  # 含選填參數
  python3 setup/add-teacher.py --name "陳佩珊" --email "vernachen327@gmail.com" --github "vernachen327" \\
      --class-code "8a" --subject "English"

  # 預覽模式（不實際執行）
  python3 setup/add-teacher.py --dry-run --name "陳佩珊" --email "vernachen327@gmail.com" --github "vernachen327"

  # 互動模式（不帶任何參數）
  python3 setup/add-teacher.py
""",
    )
    parser.add_argument("--name", help="教師姓名（繁體中文）")
    parser.add_argument("--email", help="教師 Email（須與 environment.env 的 USER_EMAIL 一致）")
    parser.add_argument("--github", help="GitHub 帳號")
    parser.add_argument("--class-code", default="", help="班級代碼（選填，例如：4c、9c）")
    parser.add_argument("--subject", default="", help="主要科目（選填，例如：English、Taiwanese）")
    parser.add_argument("--teacher-id", default="", help="Workspace 資料夾名稱（預設：Teacher_{姓名}）")
    parser.add_argument("--dry-run", action="store_true", help="預覽模式：顯示會執行的操作，不實際建立檔案")

    args = parser.parse_args()

    # 判斷是否進入互動模式
    if not args.name or not args.email or not args.github:
        if args.name or args.email or args.github:
            # 部分參數給了但不齊全
            parser.error("命令列模式須同時提供 --name、--email、--github 三個參數，或全部不給以進入互動模式。")

        # 互動模式
        print_banner()
        print_section("步驟 1：輸入教師資訊")
        print()
        print_info("必填：姓名、Email、GitHub 帳號")
        print_info("選填：班級代碼、科目（教師可稍後自行設定）")
        print()

        name = get_input("教師姓名（繁體中文）")
        email = get_input("Email（須與教師的 environment.env USER_EMAIL 一致）")
        github = get_input("GitHub 帳號")
        print()
        print_info("班級與科目為選填。教師可在自己的 workspace 中稍後建立。")
        class_code = get_optional_input("班級代碼（例如：4c、9c）")
        subject = get_optional_input("主要科目（例如：English、Taiwanese）")
        print()

        default_id = f"Teacher_{name}"
        print_info(f"預設 Workspace 資料夾名稱：{default_id}")
        teacher_id = get_optional_input("Workspace 資料夾名稱", default_id)

        teacher = AddTeacher(
            name=name,
            email=email,
            github=github,
            class_code=class_code,
            subject=subject,
            teacher_id=teacher_id,
            dry_run=args.dry_run,
        )
        # 互動模式已經印過 banner，跳過 check_admin 的重複提示
        teacher.check_admin()
        teacher.confirm_info()
        teacher.create_workspace()
        teacher.create_env_preset()
        teacher.update_acl()
        teacher.create_class_folder()
        teacher.create_teacher_branch()
        teacher.print_summary()
    else:
        # 命令列模式
        teacher = AddTeacher(
            name=args.name,
            email=args.email,
            github=args.github,
            class_code=args.class_code,
            subject=args.subject,
            teacher_id=args.teacher_id,
            dry_run=args.dry_run,
        )
        teacher.run()


if __name__ == "__main__":
    main()
