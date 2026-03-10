---
aliases:
  - David 個人品牌素材庫
  - Personal Asset Base
---

# David Personal Asset Base — 連動目錄

此資料夾透過 symlink 連結至 `~/Desktop/Personal-Asset-base/vault/`。
編輯此處的檔案等同編輯 Personal-Asset-base，反之亦然。

## 設定方式

在 Mac 終端機執行一次：

```bash
bash setup/scripts/setup-asset-link.sh
```

## 結構

```
David-personal-asset-base/
├── drafts/        → symlink → Personal-Asset-base/vault/drafts/
├── published/     → symlink → Personal-Asset-base/vault/published/
└── README.md      （此檔案，不是 symlink）
```

## 為什麼用 symlink

- Obsidian 能直接在 TeacherOS vault 裡看到並編輯文章
- 修改任一邊都即時生效（不是複製，是同一份檔案）
- 不需要背景服務、不需要 cron、零維護成本
- git 可以設定是否追蹤 symlink 內容（預設不追蹤，避免重複）
