---
name: drive
description: Google Drive 檔案操作。上傳、下載、搜尋、建立資料夾、刪除檔案。優先使用 gws CLI。
triggers:
  - 上傳到雲端
  - 同步 Drive
  - 傳到 Drive
  - 上傳 Google Drive
  - 傳到雲端
  - 下載檔案
  - 從 Drive 下載
  - 查 Drive
  - 備份到雲端
  - 備份專案
  - backup to drive
  - 同步備份
requires_args: false
args_format: "[選填：檔案路徑或操作描述]"
---

# skill: drive — Google Drive 檔案操作

上傳、下載、搜尋、管理 Google Drive 檔案與資料夾。

## 根目錄

以 Repo 根目錄為基準。gws CLI 指令參考：`ai-core/reference/gws-cli-guide.md`。

## 工具能力矩陣

| AI 能力 | 行為 |
|---------|------|
| 有終端機 + gws CLI | `gws drive +upload` / `files list/create/delete/update` |
| 無終端機 | 提醒教師手動操作，或引導使用 `publish/build.sh` |

## 執行步驟

### Step 0 — 確認 gws CLI 可用

**macOS / Linux：**
```bash
command -v gws && gws auth status
```

**Windows（PowerShell）：**
```powershell
Get-Command gws -ErrorAction SilentlyContinue && gws auth status
```

### Step 1 — 判斷操作類型

從教師指令推斷：

| 教師說 | 操作 |
|--------|------|
| 「上傳」「傳到 Drive」 | 上傳檔案 |
| 「下載」「從 Drive 拿」 | 下載檔案 |
| 「找檔案」「搜尋 Drive」 | 搜尋檔案 |
| 「建資料夾」 | 建立資料夾 |
| 「刪除」 | 刪除檔案（需教師二次確認） |

### Step 2 — 執行操作

**上傳檔案：**

若是 Markdown 轉 Word 再上傳（教學文件），優先使用 `publish/build.sh`：
```bash
./publish/build.sh <markdown_path>
```

若是直接上傳任意檔案：
```bash
gws drive +upload --file '檔案路徑' --parent FOLDER_ID
```

**下載檔案：**
```bash
# 一般檔案
gws drive files get --params '{"fileId":"FILE_ID","alt":"media"}' --output '輸出路徑'

# Google 文件匯出
gws drive files export --params '{"fileId":"FILE_ID","mimeType":"application/pdf"}' --output '輸出.pdf'
```

**搜尋檔案：**
```bash
gws drive files list --params '{"q":"name contains '\''關鍵字'\''","pageSize":20}' --format table
```

**建立資料夾：**
```bash
gws drive files create --json '{"name":"資料夾名","mimeType":"application/vnd.google-apps.folder","parents":["PARENT_ID"]}'
```

**刪除檔案（需二次確認）：**
```bash
gws drive files delete --params '{"fileId":"FILE_ID"}'
```

### Step 3 — 報告結果

回報操作結果，包含檔案名稱與 Drive 路徑。

## 注意事項

- 教學文件上傳（.md → .docx → Drive）優先走 `publish/build.sh`，該腳本已內建 gws CLI + Google Drive Desktop 雙軌切換
- 刪除操作必須向教師確認後才執行
- 檔名規則：輸出到 Google Drive 的檔案，檔名使用繁體中文（中文在前_英文原名）

---

## 備份整個 Repo 到 Google Drive

將整個 WaldorfTeacherOS Repo 備份至 Drive，Markdown 自動轉為原生 Google Doc，目錄名稱轉為中文。

### 觸發語句

| 教師說 | 操作 |
|--------|------|
| 「備份到雲端」「備份專案」 | 執行備份腳本 |
| 「backup to drive」「同步備份」 | 執行備份腳本 |

### 指令



### 選項

| 參數 | 說明 |
|------|------|
| `--dry-run` | 預覽模式：列出會處理的檔案與目錄映射，不實際上傳 |
| `--force` | 強制全部重新上傳，忽略增量比對 |
| （無參數） | 自動增量備份：只處理新增與修改的檔案 |

### 運作方式

1. 掃描 Repo 全部檔案，排除 `.git/`、`.claude/`、`node_modules/` 等系統目錄
2. `.md` 檔 → Pandoc 轉 `.docx`（使用 `publish/templates/backup-reference.docx` 範本）→ 上傳時指定 mimeType 轉為原生 Google Doc
3. 非 `.md` 檔（`.yaml`、`.py`、`.sh` 等）→ 直接上傳原檔
4. 目錄名稱依腳本內建 `FOLDER_CN_MAP` 字典轉為中文（例：`ai-core/skills/` → `AI 核心/技能/`）
5. 增量備份：透過 `publish/drive-backup-manifest.json` 記錄已上傳檔案的 mtime、size、MD5，只處理有變動的檔案
6. `setup/environment.env` 上傳前自動遮蔽含 `TOKEN`、`SECRET`、`KEY`、`PASSWORD` 的欄位值
