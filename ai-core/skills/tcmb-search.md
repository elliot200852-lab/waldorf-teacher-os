---
name: tcmb-search
description: >
  國家文化記憶庫本地索引搜尋。查詢 53,000+ 筆臺灣歷史文化素材（臺史博維護），
  回傳標題、描述、圖像 URL、授權、關鍵字。免網路，即時回應。
  當教師提到搜尋文化記憶庫、查 TCMB、找臺灣素材、搜臺灣文化、查臺灣歷史圖片時觸發。
triggers:
  - 查文化記憶庫
  - 搜尋文化記憶庫
  - TCMB
  - tcmb
  - 查 TCMB
  - 找臺灣素材
  - 搜臺灣文化
  - 查臺灣歷史
  - 查臺灣圖片
  - 文化記憶庫搜尋
  - 國家文化記憶庫
  - tcmb search
  - taiwan culture search
requires_args: true
args_format: "<搜尋關鍵字> [--limit N]"
---

# skill: tcmb-search — 國家文化記憶庫本地索引搜尋

查詢本地 TCMB（國家文化記憶庫）SQLite FTS5 索引，回傳臺灣歷史文化素材。

## 適用對象

所有教師（任何涉及臺灣相關主題的工作）。

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：嘗試 `git rev-parse --show-toplevel`。

## 前置條件

- 本地索引已建立：`~/.cache/teacheros/tcmb-local.db`
- 若索引不存在，先執行：
  ```bash
  cd workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan
  python3 tcmb_downloader.py --build --all
  ```

## 執行步驟

### Step 1 — 解析搜尋意圖

從教師的輸入中提取搜尋關鍵字。支援：
- 直接關鍵字：「/tcmb-search 達悟族」
- 自然語言：「幫我查文化記憶庫有沒有日治時期的廟宇資料」→ 關鍵字：「日治 廟宇」
- 多關鍵字：空格分隔，FTS5 會做 AND 搜尋

### Step 2 — 執行搜尋

```bash
cd {repo_root}/workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan
python3 tcmb_downloader.py --search "關鍵字" --limit 10
```

若第一次搜尋結果不理想，嘗試：
1. 拆分關鍵字（「達悟族蘭嶼」→ 分別搜「達悟族」和「蘭嶼」）
2. 使用同義詞（「原住民」→「原住民族」、「日據」→「日治」）
3. 放寬關鍵字（「赤崁樓歷史」→「赤崁樓」）

### Step 3 — 格式化結果

將搜尋結果整理為教師可直接使用的格式：

```markdown
## TCMB 搜尋結果：「{關鍵字}」

找到 N 筆相關素材：

### 1. {標題}
- 分類：{分類名}
- 描述：{描述前 100 字}...
- 圖像：{有圖/無圖}（{授權方式}）
- 關鍵字：{關鍵字標籤}
- 連結：{tcmb_url}

### 2. ...
```

### Step 4 — 教學應用建議（可選）

若教師正在備課，主動建議：
- 哪些素材適合用於當前課程
- 圖像授權是否允許課堂使用
- 相關的延伸搜尋關鍵字

## 自動觸發規則

此技能除了手動觸發外，AI 也應在以下場景**主動執行**（不需教師明確要求）：

1. 備課涉及臺灣歷史、文化、地方、族群、原住民
2. 「臺灣的故事」story pipeline 的素材搜尋階段
3. 走讀臺灣教材設計
4. 古文明神話 TW 系列（布農、泰雅、排灣、達悟）
5. 任何需要臺灣文化圖像素材的場景

## 直接 SQL 查詢（進階）

若需要更複雜的查詢（如按分類篩選、按授權篩選）：

```bash
sqlite3 ~/.cache/teacheros/tcmb-local.db \
  "SELECT title, description, tcmb_url, image_license FROM tcmb_fts f JOIN tcmb_items i ON f.rowid = i.id WHERE tcmb_fts MATCH '關鍵字' AND i.category = 'ETHNIC_AND_LANGUAGE' ORDER BY rank LIMIT 10;"
```

分類代碼：ART_AND_HUMANITY, CULTURE_AND_RELIGION, BIOGRAPHY_AND_ECOLOGY_AND_ENVIRONMENT, ETHNIC_AND_LANGUAGE, SOCIAL_AND_POLITIC, PEOPLE_AND_GROUP, SPACE_AND_GEOGRAPHY, INDUSTRY_AND_ECONOMIC, OTHER

## 索引維護

```bash
cd workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan
python3 tcmb_downloader.py --status    # 查看索引狀態
python3 tcmb_downloader.py --update    # 增量更新
```

建議每月執行一次 `--update`。
