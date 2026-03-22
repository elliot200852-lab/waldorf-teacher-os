---
aliases:
  - "三大技能深度審查 2026-03-22"
  - "deep review 暫存"
---

# TeacherOS 三大技能 Deep Review 暫存檔
> 日期：2026-03-22
> 用途：Opening 修完後，接續修 Story-Daily 和 Wrap-Up 時使用
> 完成後可刪除此檔案

---

## 一、Opening（開機技能）— 已決定修正方向，正在執行

### 決策紀錄
- 實作方式：維持技能文件修正（不建新腳本）
- Codeowner 檢查：移到 Step 2 之後
- 去重複：Opening 保留實作細節，AI_HANDOFF Step 0 簡化為參照

### 修正項目（共 10 項）
詳見計畫檔。

---

## 二、Story-Daily（臺灣的故事管線）— 待修

### Claude Code Deep Review 發現（8 嚴重 / 9 中等 / 4 低）

**嚴重問題：**
1. Step 4+5 平行化無協調機制 — 規格說「同時啟動」品質檢查與 Gemini 黑板畫，但沒有同步/等待機制。若 Step 4 失敗無法阻止 Step 5
2. Checkpoint 矩陣與實際行為矛盾 — Checkpoint 說黑板畫缺失 FAIL 停止 pipeline，但 assemble-story.js 有 fallback 繼續跑
3. Pipeline 無法在 context 耗盡後恢復 — pipeline-status.yaml 有定義但沒有「偵測是否為恢復中 pipeline」的邏輯
4. assemble-story.js exit code 處理不完整 — exit code 2 = validation failed 但腳本沒有文件化的 exit code 對照表
5. current-task.yaml 在 Step 7 刪除但 Step 8 還需要讀取 — 完成報告無法生成 metadata
6. index.yaml 並行更新的競爭條件 — 排程 + 手動同時跑會覆蓋
7. assemble-story.js 缺少圖片 base64 編碼邏輯 — HTML 輸出圖片會斷裂
8. taiwan_history_api.py 是空殼 — 只有 dataclass 定義，沒有搜尋功能

**中等問題：**
9. Step 1 自動/互動模式切換信號未定義
10. Step 2→3 輸入驗證缺失（current-task.yaml schema 未強制）
11. Step 3→4 字數下限 300 字太低（實際 650-1000 字）
12. raw-materials.md 字數檢查無 gate
13. GWS 超時後靜默跳過上傳
14. Windows GWS JSON 參數轉義未測試
15. index.yaml 路徑用 / 硬寫
16. chalkboard-prompt.md 下載檔名更新有競爭條件
17. source URL 解析預期完整 URL 但 session.yaml 記錄縮寫代碼

**低等問題：**
18. 自動編號邏輯只有描述沒有實作
19. 圖片 URL 無有效性驗證
20. Obsidian alias 同步未納入管線
21. 版本管理 v1/v2 的 index.yaml schema 不一致

### Cowork Deep Review 補充

- 整體 8.5/10，管線設計完善
- **P0**: 確認 `-v2-v2-` 檔名是 bug（assemble-story.js 版本號拼接邏輯重複）
- **P0**: story-archive 在 A005 前做一次 dry-run 驗證
- **P0**: 確認 assemble-story.js 黑板畫 4 層搜尋策略是否已實現
- **P1**: 前置驗證與 checkpoint 擇一保留，消除冗餘
- **P1**: 排程模式做一次實際驗證（特別是 Step 5 Gemini 瀏覽器 fallback）
- **P1**: 版本標記方式三方統一（index / session / quality-log）
- **P2**: checkpoint 輸出格式強制帶檔案大小
- **P2**: Gemini 中文前綴觸發機制驗證

### 資料流完整性

| 步驟 | 輸入驗證 | 輸出驗證 | 狀態 |
|------|----------|----------|------|
| Step 0-1 選題 | 缺失 | 缺失 | 脆弱 |
| Step 2 研究 | 缺失 | 缺失 | 脆弱 |
| Step 3 撰寫 | 部分 | 部分 | 脆弱 |
| Step 4 品檢 | 存在 | 存在 | OK |
| Step 5 黑板畫 | 弱 | 弱 | 脆弱 |
| Step 6 組裝 | 部分 | 部分 | 有問題 |
| Step 7 歸檔 | 存在 | 存在 | OK |

---

## 三、Wrap-Up（收工技能）— 待修

### Claude Code Deep Review 發現（1 嚴重 / 9 中等 / 3 低）

**嚴重問題：**
1. git push 失敗後 rebase 錯誤處理不完整 — rebase 衝突無定義處理、subagent 可能沒有 context 解決衝突、沒有 rollback 機制

**中等問題：**
2. 班級推斷邏輯未定義 — 若教師未指定班級，如何從對話推斷？無演算法
3. commit message 格式未標準化 — 只說「簡潔中文備註」
4. pre-commit hook 攔截後的部分 commit 語義不明
5. Python3 跨平台偵測缺失 — obsidian-check.py 硬寫 python3
6. marker 檔案競爭條件 — Phase A 平行化時兩個 subagent 可能同時觸碰 .last-obsidian-check
7. 「靜默通過」隱藏部分失敗 — Obsidian 修正部分失敗時不報告
8. subagent 回傳契約未定義 — Phase A 兩個 subagent 該回傳什麼格式
9. git index 並行操作的競爭條件 — 兩個 subagent 同時 git add
10. wrap-up → opening 的狀態驗證缺失 — 若 session.yaml 被寫壞 opening 無法偵測

**低等問題：**
11. confirmed_decisions 附加邏輯缺乏去重
12. 路徑分隔符 Windows 正規化
13. context health 判斷閾值可以更精準

### Cowork Deep Review 補充

- **P0**: Push 失敗處理完整化：最多重試 2 次、rebase 衝突時停止並報告
- **P0**: Pre-commit hook 攔截時機提前到 Step 1（驗證授權範圍）
- **P0**: 多班級工作線失敗時的繼續/停止邏輯
- **P0**: Subagent 平行化要麼實現觸發邏輯，要麼改為序列並移除承諾
- **P1**: Obsidian marker 要麼在 opening 補上檢查邏輯，要麼移除
- **P1**: sync-agents 自動觸發條件需定義
- **P1**: Git branch 檢查加入 Step 4a
- **P1**: last_updated 加時區或改用 ISO 8601
- **P2**: Commit message 格式規範化
- **P2**: 教師中途取消的回滾機制

### 跨技能共通問題（Cowork 提出）

1. 跨平台實施全靠文字描述，缺乏統一 Python 執行層 — 建議建立 platform-utils.py
2. Subagent / 平行化承諾 > 實際實現 — 需統一決定：技能層實現還是 AI agent 層判斷
3. Obsidian marker 是孤兒機制 — wrap-up 寫、opening 不讀、session-guard hook 不存在。三端斷裂
