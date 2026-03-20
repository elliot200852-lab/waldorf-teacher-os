---
name: check-compat
description: "跨平台相容性檢查。掃描 TeacherOS Repo 中所有 .py、.sh、skill .md、hook，依 6 條規則產出嚴重度分級報告。當 David 說「跨平台檢查」「check compat」「平台檢查」「相容性檢查」「檢查相容性」，或提到跨平台問題、Windows 相容、技術債清理時觸發。也適用於分享架構給夥伴之前的預檢。"
triggers:
  - 跨平台檢查
  - check compat
  - 平台檢查
  - 相容性檢查
  - 檢查相容性
  - platform check
  - 技術債檢查
requires_args: false
---

# skill: check-compat — 跨平台相容性檢查

全 Repo 跨平台健檢工具。掃描 Python、Shell、技能 .md、Hook，依 6 條規則產出報告。

## 觸發條件

- David 說「跨平台檢查」「check compat」或類似意思
- 準備把架構分享給 Windows/Linux 上的夥伴
- 定期維護（建議每月一次）
- 做完一輪開發想確認沒有引入平台問題

## 執行步驟

### Step 1 — 執行掃描

依教師指示選擇模式：

**完整掃描（預設）：**

```bash
python3 setup/scripts/check-compat.py
```

```powershell
python3 setup/scripts/check-compat.py
```

**快速模式（只看高風險）：**

```bash
python3 setup/scripts/check-compat.py --quick
```

```powershell
python3 setup/scripts/check-compat.py --quick
```

**單檔模式（指定檔案）：**

```bash
python3 setup/scripts/check-compat.py path/to/file.py
```

```powershell
python3 setup/scripts/check-compat.py path/to/file.py
```

### Step 2 — 呈現報告

將掃描結果呈現給教師，依嚴重度分組：

- 🔴 高：在其他平台上會直接報錯（硬編碼路徑）
- 🟡 中：在其他平台上行為不同或需要額外處理
- 🟢 低：不影響功能，改善後維護更輕鬆（os.path → pathlib 風格建議）

### Step 3 — 建議修復順序

根據報告內容，建議教師：

1. **立即修復**：🔴 高風險項目
2. **下次迭代**：🟡 中風險項目
3. **長期改善**：🟢 低風險項目

如果教師要求修復，逐一確認後再動手。每次修復後重跑掃描確認。

## 檢查規則

| 規則 | 嚴重度 | 偵測內容 |
|------|--------|---------|
| 1 | 🔴 高 | 硬編碼路徑（/Users/、C:\、/opt/homebrew） |
| 1b | 🟢 低 | os.path 用法（建議改 pathlib，但功能上安全） |
| 2 | 🟡 中 | 平台限定指令（subprocess 中的 sed/grep；skill bash block 缺 PowerShell） |
| 3 | 🟡 中 | 未遷移 Shell 腳本（cross-platform.yaml status: active） |
| 4 | 🟡 中 | Python 環境假設（Unix-only 模組、硬編碼 shebang） |
| 5 | 🟡 中 | Hook 安全性（缺 shebang、未委派 Python） |
| 6 | 🟢 低 | 換行符（.gitattributes 是否存在） |

## 注意事項

- 本技能只做診斷，不自動修改任何檔案
- 掃描器排除：.git、node_modules、venv、__pycache__、temp、Tool Download
- 掃描器也排除自身（check-compat.py），避免規則定義觸發 false positive
- 修正參考：`ai-core/reference/cross-platform.yaml`
- 技能指引：`ai-core/skills/README.md` Step 2
