"""
TeacherOS 跨平台抽象層 (Platform Abstraction Layer) — 參考草稿
================================================================

狀態：不引入、不 import、不使用。
保留原因：未來 Repo 規模擴大時的設計參考。

評估結論（2026-03-20）：
  - Python stdlib（pathlib、shutil、tempfile、subprocess）已是跨平台抽象層
  - 再包一層 wrapper 對 ~15 支腳本的 Repo 而言成本 > 收益
  - 若未來 Python 腳本超過 30 支且出現重複邏輯，可重新評估

原始來源：Chat 對話草稿（David 提供）
"""

import os
import sys
import shutil
import subprocess
import platform as _platform
from pathlib import Path
from typing import Optional, Union, List, Dict, Any


# ============================================================
# 第一層：平台偵測
# ============================================================

class Platform:
    """平台資訊的唯一查詢點"""

    @staticmethod
    def system() -> str:
        """回傳標準化平台名稱：'macos' | 'windows' | 'linux'"""
        s = _platform.system().lower()
        if s == "darwin":
            return "macos"
        elif s == "windows":
            return "windows"
        else:
            return "linux"

    @staticmethod
    def is_macos() -> bool:
        return Platform.system() == "macos"

    @staticmethod
    def is_windows() -> bool:
        return Platform.system() == "windows"

    @staticmethod
    def is_linux() -> bool:
        return Platform.system() == "linux"

    @staticmethod
    def home() -> Path:
        """使用者家目錄，跨平台安全"""
        return Path.home()

    @staticmethod
    def shell_name() -> str:
        """目前系統預設 shell"""
        if Platform.is_windows():
            return "powershell"
        return os.environ.get("SHELL", "/bin/bash").split("/")[-1]

    @staticmethod
    def summary() -> Dict[str, str]:
        """回傳平台摘要，供除錯或日誌使用"""
        return {
            "system": Platform.system(),
            "shell": Platform.shell_name(),
            "home": str(Platform.home()),
            "python": sys.version.split()[0],
            "arch": _platform.machine(),
        }


# ============================================================
# 第二層：路徑處理
# ============================================================

class Paths:
    """
    所有路徑操作的跨平台工具箱。
    規則：所有方法都回傳 pathlib.Path，永不回傳 str。
    """

    @staticmethod
    def resolve(path_str: str, base: Optional[Path] = None) -> Path:
        """
        智慧路徑解析：
        - ~ 展開為家目錄
        - 相對路徑以 base 為基準（預設為 cwd）
        - 自動處理 Windows 反斜線
        """
        path_str = path_str.replace("\\", "/")
        p = Path(path_str).expanduser()
        if not p.is_absolute():
            base = base or Path.cwd()
            p = base / p
        return p.resolve()

    @staticmethod
    def workspace_root(marker: str = "TeacherOS.yaml") -> Optional[Path]:
        """
        從 cwd 往上搜尋 workspace 根目錄。
        以 marker 檔案的存在作為識別依據。
        """
        current = Path.cwd()
        for parent in [current, *current.parents]:
            if (parent / marker).exists():
                return parent
        return None

    @staticmethod
    def ensure_dir(path: Path) -> Path:
        """確保目錄存在，回傳該路徑"""
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def safe_copy(src: Path, dst: Path, overwrite: bool = False) -> Path:
        """
        跨平台安全複製。
        - 自動建立目標目錄
        - overwrite=False 時，目標存在會報錯
        """
        if not src.exists():
            raise FileNotFoundError(f"來源不存在：{src}")
        if dst.exists() and not overwrite:
            raise FileExistsError(f"目標已存在（設 overwrite=True 覆蓋）：{dst}")
        Paths.ensure_dir(dst.parent)
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return dst

    @staticmethod
    def glob_recursive(root: Path, pattern: str) -> List[Path]:
        """遞迴 glob，回傳排序後的路徑清單"""
        return sorted(root.rglob(pattern))

    @staticmethod
    def relative_to_workspace(path: Path) -> str:
        """嘗試轉為相對於 workspace 的路徑字串，找不到 workspace 就回傳絕對路徑"""
        ws = Paths.workspace_root()
        if ws:
            try:
                return str(path.resolve().relative_to(ws))
            except ValueError:
                pass
        return str(path.resolve())


# ============================================================
# 第三層：Shell 指令抽象
# ============================================================

class Shell:
    """
    跨平台 shell 操作。
    設計原則：能用 Python 做的就不呼叫 shell。
    這裡只封裝那些「不得不呼叫外部指令」的情境。
    """

    @staticmethod
    def run(
        cmd: Union[str, List[str]],
        cwd: Optional[Path] = None,
        capture: bool = True,
        check: bool = True,
        timeout: int = 60,
    ) -> subprocess.CompletedProcess:
        """
        跨平台執行指令。
        - cmd 可以是字串或清單
        - 字串模式下自動選擇 shell（bash / powershell）
        - 回傳 CompletedProcess，capture=True 時可取 stdout/stderr
        """
        kwargs: Dict[str, Any] = {
            "cwd": str(cwd) if cwd else None,
            "capture_output": capture,
            "text": True,
            "timeout": timeout,
        }

        if isinstance(cmd, str):
            kwargs["shell"] = True
            if Platform.is_windows():
                cmd = f'powershell -NoProfile -Command "{cmd}"'

        if check:
            return subprocess.run(cmd, check=True, **kwargs)
        else:
            return subprocess.run(cmd, **kwargs)

    @staticmethod
    def which(tool: str) -> Optional[Path]:
        """
        查詢工具是否可用，回傳路徑或 None。
        取代 shell 的 which / where 指令。
        """
        result = shutil.which(tool)
        return Path(result) if result else None

    @staticmethod
    def require(tool: str) -> Path:
        """查詢工具，不存在就報錯"""
        path = Shell.which(tool)
        if path is None:
            raise EnvironmentError(
                f"必要工具 '{tool}' 未安裝或不在 PATH 中。\n"
                f"平台：{Platform.system()}｜Shell：{Platform.shell_name()}"
            )
        return path

    @staticmethod
    def git(args: str, cwd: Optional[Path] = None) -> str:
        """
        Git 指令的便捷封裝。
        回傳 stdout 字串（已 strip）。
        """
        Shell.require("git")
        result = Shell.run(f"git {args}", cwd=cwd)
        return result.stdout.strip() if result.stdout else ""

    @staticmethod
    def open_file(path: Path) -> None:
        """用系統預設程式開啟檔案（跨平台）"""
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError(f"檔案不存在：{path}")
        if Platform.is_macos():
            subprocess.Popen(["open", str(path)])
        elif Platform.is_windows():
            os.startfile(str(path))  # type: ignore
        else:
            subprocess.Popen(["xdg-open", str(path)])


# ============================================================
# 第四層：文字處理（CJK 相關）
# ============================================================

class Text:
    """TeacherOS 常用的文字處理工具"""

    @staticmethod
    def is_cjk(char: str) -> bool:
        """判斷是否為 CJK 字元"""
        cp = ord(char)
        return any([
            0x4E00 <= cp <= 0x9FFF,    # CJK Unified Ideographs
            0x3400 <= cp <= 0x4DBF,    # CJK Extension A
            0x20000 <= cp <= 0x2A6DF,  # CJK Extension B
            0xF900 <= cp <= 0xFAFF,    # CJK Compatibility Ideographs
            0x3000 <= cp <= 0x303F,    # CJK Symbols and Punctuation
            0xFF00 <= cp <= 0xFFEF,    # Fullwidth Forms
        ])

    @staticmethod
    def wrap_cjk(text: str, font_tag: str = "CJK") -> str:
        """
        為 reportlab 用：將 CJK 字元用 <font> 標籤包裹。
        用於 git-history 的 PDF 輸出等場景。
        """
        result = []
        in_cjk = False
        for char in text:
            if Text.is_cjk(char):
                if not in_cjk:
                    result.append(f'<font name="{font_tag}">')
                    in_cjk = True
                result.append(char)
            else:
                if in_cjk:
                    result.append("</font>")
                    in_cjk = False
                result.append(char)
        if in_cjk:
            result.append("</font>")
        return "".join(result)


# ============================================================
# 自我診斷（直接執行此檔案時）
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TeacherOS Platform Abstraction Layer — 自我診斷")
    print("=" * 60)

    info = Platform.summary()
    for k, v in info.items():
        print(f"  {k}: {v}")

    ws = Paths.workspace_root()
    print(f"\n  workspace: {ws or '（未偵測到 TeacherOS.yaml）'}")

    print("\n  工具檢查：")
    for tool in ["git", "python3", "node", "gws"]:
        path = Shell.which(tool)
        status = f"OK {path}" if path else "NOT FOUND"
        print(f"    {tool}: {status}")

    print("\n診斷完成。")
