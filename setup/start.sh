#!/bin/bash
# TeacherOS 快速啟動 — macOS / Linux 入口
# 檢查 Python 3，然後呼叫 quick-start.py

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 檢查 Python 3
if ! command -v python3 &>/dev/null; then
  echo ""
  echo "  TeacherOS 需要 Python 3 才能執行。"
  echo ""
  if command -v brew &>/dev/null; then
    echo "  偵測到 Homebrew，正在安裝 Python 3..."
    brew install python3
  else
    echo "  請安裝 Python 3："
    echo "    https://www.python.org/downloads/"
    echo ""
    echo "  macOS 也可以先安裝 Homebrew，再執行此腳本："
    echo "    /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
  fi
fi

echo ""
echo "  Python 3 已就緒：$(python3 --version)"
echo ""

python3 "$SCRIPT_DIR/quick-start.py" "$@"
