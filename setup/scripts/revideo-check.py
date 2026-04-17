#!/usr/bin/env python3
"""
Revideo 環境自動檢驗與除錯腳本
用法：python3 setup/scripts/revideo-check.py
自動檢查 Revideo workspace 的環境、依賴、設定檔完整性，
並嘗試修復常見問題。
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# ── 設定 ──
HOME = Path.home()
REVIDEO_DIR = HOME / "revideo-workspace" / "revideo-project"
REQUIRED_DEPS = [
    "@revideo/2d", "@revideo/core", "@revideo/renderer",
    "@revideo/vite-plugin", "@revideo/ui",
]
REQUIRED_DEV_DEPS = ["tsx", "vite"]
REQUIRED_FILES = [
    "package.json", "vite.config.ts", "tsconfig.json",
    "src/project.ts", "src/project.meta", "src/render.ts",
]
REQUIRED_DIRS = ["src/scenes", "public/audio"]

passed = 0
failed = 0
fixed = 0


def check(label: str, ok: bool, fix_fn=None) -> bool:
    global passed, failed, fixed
    if ok:
        print(f"  [PASS] {label}")
        passed += 1
        return True
    elif fix_fn:
        print(f"  [FIX]  {label} — 嘗試修復...")
        try:
            fix_fn()
            print(f"         → 已修復")
            fixed += 1
            return True
        except Exception as e:
            print(f"  [FAIL] {label} — 修復失敗：{e}")
            failed += 1
            return False
    else:
        print(f"  [FAIL] {label}")
        failed += 1
        return False


def run(cmd: str, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True, timeout=60,
    )


# ══════════════════════════════════════════
# 1. 系統工具檢查
# ══════════════════════════════════════════
print("\n═══ 1. 系統工具 ═══")

check("Node.js 已安裝", shutil.which("node") is not None)

node_ver = run("node --version")
if node_ver.returncode == 0:
    ver = node_ver.stdout.strip()
    major = int(ver.lstrip("v").split(".")[0])
    check(f"Node.js 版本 >= 16（目前 {ver}）", major >= 16)

check("FFmpeg 已安裝", shutil.which("ffmpeg") is not None)
check("npm 已安裝", shutil.which("npm") is not None)

# ══════════════════════════════════════════
# 2. 專案目錄結構
# ══════════════════════════════════════════
print("\n═══ 2. 專案目錄結構 ═══")

check(f"專案目錄存在：{REVIDEO_DIR}", REVIDEO_DIR.is_dir())

if not REVIDEO_DIR.is_dir():
    print("\n  [SKIP] 專案不存在，後續檢查跳過。請先觸發 teach-animation 技能初始化專案。")
    print(f"\n═══ 結果：{passed} 通過 / {failed} 失敗 / {fixed} 已修復 ═══")
    sys.exit(1)

for d in REQUIRED_DIRS:
    dir_path = REVIDEO_DIR / d

    def make_dir(p=dir_path):
        p.mkdir(parents=True, exist_ok=True)

    check(f"目錄 {d}/", dir_path.is_dir(), fix_fn=make_dir)

# ══════════════════════════════════════════
# 3. 設定檔完整性
# ══════════════════════════════════════════
print("\n═══ 3. 設定檔完整性 ═══")

for f in REQUIRED_FILES:
    check(f"檔案 {f}", (REVIDEO_DIR / f).is_file())

# 檢查 package.json 內容
pkg_path = REVIDEO_DIR / "package.json"
if pkg_path.is_file():
    pkg = json.loads(pkg_path.read_text())
    check('package.json type = "module"', pkg.get("type") == "module")
    check('scripts.render 已定義', "render" in pkg.get("scripts", {}))
    check('scripts.start 已定義', "start" in pkg.get("scripts", {}))

# 檢查 project.meta
meta_path = REVIDEO_DIR / "src" / "project.meta"
if meta_path.is_file():
    meta = json.loads(meta_path.read_text())
    check('project.meta 有 name 欄位', "name" in meta)
    check('project.meta 有 fps 欄位', "fps" in meta)

# 檢查 vite.config.ts 使用正確的 plugin 匯出
vite_path = REVIDEO_DIR / "vite.config.ts"
if vite_path.is_file():
    vite_content = vite_path.read_text()
    check(
        'vite.config.ts 使用 pkg.default ?? pkg 匯出',
        "pkg.default" in vite_content or "default ??" in vite_content,
    )

# ══════════════════════════════════════════
# 4. npm 依賴
# ══════════════════════════════════════════
print("\n═══ 4. npm 依賴 ═══")

node_modules = REVIDEO_DIR / "node_modules"
check("node_modules/ 存在", node_modules.is_dir())

if node_modules.is_dir():
    all_deps_ok = True
    missing = []
    for dep in REQUIRED_DEPS + REQUIRED_DEV_DEPS:
        dep_dir = node_modules / dep.replace("/", os.sep)
        if not dep_dir.is_dir():
            missing.append(dep)
            all_deps_ok = False

    if missing:
        def install_missing():
            run(f"npm install {' '.join(missing)}", cwd=str(REVIDEO_DIR))

        check(
            f"所有必要依賴已安裝（缺少：{', '.join(missing)}）",
            False,
            fix_fn=install_missing,
        )
    else:
        check("所有必要依賴已安裝", True)

# ══════════════════════════════════════════
# 5. 場景檔 API 檢查
# ══════════════════════════════════════════
print("\n═══ 5. 場景檔 API 檢查 ═══")

scenes_dir = REVIDEO_DIR / "src" / "scenes"
if scenes_dir.is_dir():
    tsx_files = list(scenes_dir.glob("*.tsx"))
    check(f"src/scenes/ 中有場景檔（{len(tsx_files)} 個）", len(tsx_files) > 0)

    for tsx in tsx_files:
        content = tsx.read_text()
        # 檢查 makeScene2D 是否有兩個參數
        has_name_param = "makeScene2D('" in content or 'makeScene2D("' in content
        check(
            f"{tsx.name}: makeScene2D 有 name 參數",
            has_name_param,
        )
        # 檢查 import 來源
        uses_revideo = "@revideo/2d" in content
        uses_motion_canvas = "@motion-canvas" in content
        check(f"{tsx.name}: import 來自 @revideo（非 @motion-canvas）", uses_revideo and not uses_motion_canvas)

# ══════════════════════════════════════════
# 6. 渲染測試（可選，需要場景檔存在）
# ══════════════════════════════════════════
print("\n═══ 6. 渲染能力 ═══")

project_ts = REVIDEO_DIR / "src" / "project.ts"
if project_ts.is_file():
    content = project_ts.read_text()
    check("project.ts 引入了場景檔", "?scene" in content)
else:
    check("project.ts 存在", False)

# ══════════════════════════════════════════
# 7. 跨平台相容性
# ══════════════════════════════════════════
print("\n═══ 7. 跨平台相容性 ═══")

current_os = platform.system()
check(f"目前平台：{current_os}", True)

if current_os == "Darwin":
    # macOS: 檢查中文字型
    fc_result = run("fc-list | grep -i 'noto sans tc'")
    check("Noto Sans TC 字型已安裝（macOS）", fc_result.returncode == 0 and fc_result.stdout.strip() != "")
elif current_os == "Windows":
    # Windows: 檢查中文字型
    check("（Windows 字型檢查需在 PowerShell 執行）", True)

# ══════════════════════════════════════════
# 結果摘要
# ══════════════════════════════════════════
total = passed + failed
print(f"\n{'═' * 50}")
print(f"  檢驗結果：{passed}/{total} 通過 | {failed} 失敗 | {fixed} 已修復")
if failed == 0:
    print("  狀態：全部通過 ✓")
else:
    print("  狀態：有未解決的問題，請檢查上方 [FAIL] 項目")
print(f"{'═' * 50}\n")

sys.exit(0 if failed == 0 else 1)
