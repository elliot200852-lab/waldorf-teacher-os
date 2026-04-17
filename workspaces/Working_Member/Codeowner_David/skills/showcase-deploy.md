---
aliases:
  - "素材展示部署"
name: showcase-deploy
type: personal-skill
description: >
  將 HTML 素材上傳至 Google Drive「其他素材」並觸發 david-showcase GitHub Pages 部署。
  自動判斷子資料夾歸屬，無匹配則建立新資料夾。
triggers:
  - 上傳展示
  - 素材展示
  - deploy showcase
  - showcase
  - 放到展示頁
  - 上傳到 showcase
  - 上傳素材
  - 發布到展示
requires_args: false
author: David
created: 2026-04-11
---

# skill: showcase-deploy — 素材展示部署

將 HTML 檔案上傳至 Google Drive「其他素材」資料夾，觸發 david-showcase 部署至 GitHub Pages。

**站點**：https://elliot200852-lab.github.io/david-showcase/
**Repo**：`elliot200852-lab/david-showcase`
**Drive 根資料夾 ID**：`1rK3Eq8LH2Sg9YRBUcPA6PzQhDzVckLCq`

---

## 預授權操作

以下操作已獲得完整預授權，AI 直接執行，不逐一詢問：

- gws Drive 檔案列表查詢、資料夾建立、檔案上傳
- `gh workflow run` 觸發部署
- 對話中已產出的 HTML 檔案讀取

---

## 執行流程

### Step 1 — 確認 HTML 檔案

從以下來源定位要上傳的 HTML 檔案（依優先順序）：

1. 教師明確指定路徑（如「上傳展示 /path/to/file.html」）
2. 本次對話中剛產出的 HTML 檔案
3. 教師指定的 .md 檔案 → 先用 beautify 技能轉為 HTML

若無法定位，詢問教師：「要上傳哪個檔案？」（僅此一次確認）

### Step 2 — 列出 Drive 現有子資料夾

```bash
/opt/homebrew/bin/gws drive files list \
  --params '{"q":"'\''1rK3Eq8LH2Sg9YRBUcPA6PzQhDzVckLCq'\'' in parents and mimeType='\''application/vnd.google-apps.folder'\'' and trashed=false","orderBy":"name"}' \
  --fields 'files(id,name)'
```

### Step 3 — 判斷目標子資料夾

**自動匹配邏輯**（依 HTML 檔案的來源脈絡判斷）：

| 脈絡線索 | 匹配目標 |
|----------|---------|
| 9C 英文相關 | `*9C英文*` |
| 走讀臺灣/台南/台中 | `*走讀*` |
| 歷史/台灣史/現代史 | `*歷史*` |
| 台灣文學/9D 主課程 | `*台灣文學*` |
| 工作坊/教學示範 | `*工作坊*` |
| TeacherOS/系統 | `*TeacherOS*` |

匹配規則：
- 用檔名與當前工作脈絡（班級、科目）比對現有資料夾名稱
- **命中** → 使用該資料夾 ID
- **未命中** → 進入 Step 3b 建立新資料夾

### Step 3b — 建立新子資料夾

命名格式：`{下一個序號}_{描述}`

序號規則：取現有最大序號 + 1，兩位數零填充（如 `07`、`12`）。

```bash
/opt/homebrew/bin/gws drive files create \
  --json '{"name":"{序號}_{描述}","mimeType":"application/vnd.google-apps.folder","parents":["1rK3Eq8LH2Sg9YRBUcPA6PzQhDzVckLCq"]}'
```

描述由 AI 根據檔案內容自動產生（簡短中文，如「9D台灣文學」「五年級植物學」）。

### Step 4 — 上傳 HTML 至目標資料夾

檔名規則：保留原檔名。若原檔名純英文或不夠直覺，改為繁體中文描述性檔名。

```bash
/opt/homebrew/bin/gws drive files create \
  --json '{"name":"{檔名}.html","parents":["{FOLDER_ID}"]}' \
  --upload '{本地 HTML 路徑}' \
  --upload-content-type 'text/html'
```

### Step 5 — 觸發 GitHub Pages 部署

```bash
gh workflow run deploy.yml --repo elliot200852-lab/david-showcase
```

### Step 6 — 回報

```
── showcase-deploy 完成 ──
  檔案：{檔名}
  資料夾：{子資料夾名稱}（{新建/既有}）
  Drive：已上傳
  部署：已觸發（約 2-3 分鐘後生效）
  站點：https://elliot200852-lab.github.io/david-showcase/
```

---

## 錯誤處理

| 狀況 | 處理 |
|------|------|
| gws 未連線（401） | 提示：「gws 未連線，請自行安裝 gws CLI（`npm install -g @googleworkspace/cli`）並執行 `gws auth login` 完成登入。」停止。 |
| HTML 檔案不存在 | 回報路徑錯誤，請教師確認 |
| gh CLI 無權限 | 提示教師確認 GitHub 登入狀態 |
| Drive 上傳失敗 | 回報錯誤訊息，建議重試 |

---

## 批次模式

教師說「上傳展示 A B C」或「這幾個都放到展示頁」時，對每個檔案重複 Step 1-4，最後統一觸發一次部署（Step 5）。
