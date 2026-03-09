---
name: save
description: 儲存教師工作並上傳至 GitHub。執行 git add + commit + push，將所有變更安全備份到遠端。
triggers:
  - 存檔
  - 儲存
  - 幫我存
  - commit
  - 上傳
  - 備份今天的工作
requires_args: false
args_format: "[選填：儲存說明]"
---

# skill: save — 儲存工作並上傳

將教師目前所有的檔案變更儲存並上傳至 GitHub。

## 執行步驟

### Step 1 — 檢查是否有變更

執行 `git status`，確認是否有未儲存的更動。

- 若沒有任何更動，回應：「目前沒有新的更動，不需要存檔。」
- 若有更動，列出變更的檔案（用簡單的中文描述，不顯示原始 git 輸出）

範例回應：
> 「你目前有 3 個檔案有更動：Unit 2 教案、學生 DI 分類、進度紀錄。要幫你存檔嗎？」

### Step 1.5 — Obsidian 標籤自動檢查

執行 `python3 setup/scripts/obsidian-check.py --staged-only`

- 若有未標籤的新增 .md 檔：自動為其加上中文 aliases frontmatter（根據路徑與前 30 行內容產生）
- 若有未標籤的新增 .yaml 檔：自動為其加上中文標頭註解
- 若有未收錄 HOME.md 的新增檔案：自動插入 HOME.md 對應區段
- 標籤完成後，將新修改的檔案加入暫存區（`git add` 受影響的檔案）
- 若無新增檔案需要處理：跳過此步驟（零延遲）

### Step 2 — 產出儲存說明

若教師在觸發時已提供說明（例如「儲存，備註是完成 Unit 2」），直接使用。

若未提供，**AI 自行根據變更內容摘要產出簡潔中文備註，不需詢問教師。**
直接進入 Step 3。

### Step 3 — 執行存檔

依序執行：

```bash
git add .
git commit -m "[教師提供的說明]"
git push
```

### Step 4 — 確認結果

執行成功後回應：
> 「已存檔完成！備註：[說明]。你的工作已安全上傳到 GitHub。」

若 push 失敗（例如遠端有更新），嘗試：

```bash
git pull --rebase
git push
```

若仍失敗，用簡單語言向教師說明狀況，並建議聯絡 David。

## 注意事項

- 不要顯示原始 git 輸出給教師，用中文摘要即可
- pre-commit hook 會自動檢查權限，若被攔截，向教師解釋哪些檔案超出授權範圍
- 此技能不更新各科目 session.yaml 的進度欄位——那是 session-end 的工作
- 建議教師在使用 session-end（收尾）之後再使用 save（存檔），確保進度紀錄也一起上傳
