#!/usr/bin/env python3
"""
tcmb_downloader.py — 國家文化記憶庫本地索引建立器
================================================
從 TCMB Open Dataset API 下載全部素材 metadata，
建立本地 SQLite FTS5 全文索引，供 taiwan_history_api.py 離線搜尋。

API 端點（免費、不需 Key、不需固定 IP）：
  https://tcmbdata.culture.tw/opendata/dataSet/culture?subject={CODE}

九大分類：
  ART_AND_HUMANITY, CULTURE_AND_RELIGION, BIOGRAPHY_AND_ECOLOGY_AND_ENVIRONMENT,
  ETHNIC_AND_LANGUAGE, SOCIAL_AND_POLITIC, PEOPLE_AND_GROUP,
  SPACE_AND_GEOGRAPHY, INDUSTRY_AND_ECONOMIC, OTHER

Author: TeacherOS / David
License: MIT
"""

import argparse
import json
import logging
import re
import sqlite3
import ssl
import sys
import time
import urllib3
from datetime import datetime
from pathlib import Path

try:
    import requests
    from requests.adapters import HTTPAdapter
except ImportError:
    print("請先安裝 requests: pip install requests --break-system-packages")
    raise

# tcmbdata.culture.tw 的 SSL 憑證缺少 Subject Key Identifier，
# Python 3.14+ 預設會拒絕。建立寬鬆 SSL adapter 來處理此政府網站。
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class _TcmbSSLAdapter(HTTPAdapter):
    """對 tcmbdata.culture.tw 使用寬鬆 SSL 驗證"""
    def send(self, request, **kwargs):
        kwargs["verify"] = False
        return super().send(request, **kwargs)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("tcmb_downloader")

# ─────────────────────────────────────────────
# 常數
# ─────────────────────────────────────────────

BASE_URL = "https://tcmbdata.culture.tw/opendata/dataSet/culture"

CATEGORIES = {
    "ART_AND_HUMANITY":                       "藝術與人文",
    "CULTURE_AND_RELIGION":                   "民俗與宗教",
    "BIOGRAPHY_AND_ECOLOGY_AND_ENVIRONMENT":  "生物、生態與環境",
    "ETHNIC_AND_LANGUAGE":                    "族群與語言",
    "SOCIAL_AND_POLITIC":                     "社會與政治",
    "PEOPLE_AND_GROUP":                       "人物與團體",
    "SPACE_AND_GEOGRAPHY":                    "空間、地域與遷徙",
    "INDUSTRY_AND_ECONOMIC":                  "產業與經濟",
    "OTHER":                                  "其他",
}

DB_DIR = Path.home() / ".cache" / "teacheros"
DB_PATH = DB_DIR / "tcmb-local.db"
API_PAGE_SIZE = 20   # API 固定每頁 20 筆，無法調整
REQUEST_DELAY = 0.3  # 秒，避免過度請求


# ─────────────────────────────────────────────
# 資料庫初始化
# ─────────────────────────────────────────────

def init_db(conn: sqlite3.Connection):
    """建立資料表與 FTS5 索引"""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tcmb_items (
            id INTEGER PRIMARY KEY,
            identifier TEXT,
            index_code TEXT,
            image_license TEXT,
            content_license TEXT,
            title TEXT,
            description TEXT,
            original_url TEXT,
            create_dept TEXT,
            last_update_date TEXT,
            images TEXT,
            subjects TEXT,
            keywords TEXT,
            tcmb_url TEXT,
            category TEXT
        );

        CREATE TABLE IF NOT EXISTS download_log (
            category TEXT PRIMARY KEY,
            total_records INTEGER,
            downloaded_at TEXT,
            duration_seconds REAL
        );
    """)

    # FTS5 虛擬表（若不存在才建立）
    try:
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS tcmb_fts USING fts5(
                title, description, keywords,
                content='tcmb_items',
                content_rowid='id'
            );
        """)
    except sqlite3.OperationalError:
        pass  # 已存在

    conn.commit()


def strip_html(text: str) -> str:
    """移除 HTML 標籤"""
    if not text:
        return ""
    return re.sub(r'<[^>]+>', '', text).strip()


# ─────────────────────────────────────────────
# 下載邏輯
# ─────────────────────────────────────────────

def download_category(session: requests.Session, subject_code: str) -> list[dict]:
    """下載單一分類的全部資料（使用 page 參數分頁，每頁固定 20 筆）"""
    all_rows = []
    seen_ids = set()  # 去重：API 偶有重複

    # 先查 total
    resp = session.get(BASE_URL, params={"subject": subject_code, "page": 1}, timeout=30)
    resp.raise_for_status()
    first_data = resp.json()
    total = first_data.get("total", 0)

    if total == 0:
        logger.info(f"  {CATEGORIES.get(subject_code, subject_code)}：0 筆，跳過")
        return []

    total_pages = (total + API_PAGE_SIZE - 1) // API_PAGE_SIZE
    logger.info(f"  {CATEGORIES.get(subject_code, subject_code)}：共 {total:,} 筆（{total_pages} 頁），開始下載...")

    # 處理第一頁
    for row in first_data.get("rows", []):
        rid = row.get("id")
        if rid not in seen_ids:
            seen_ids.add(rid)
            all_rows.append(row)

    page = 2
    while page <= total_pages:
        params = {"subject": subject_code, "page": page}
        resp = session.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("rows", [])
        if not rows:
            break

        for row in rows:
            rid = row.get("id")
            if rid not in seen_ids:
                seen_ids.add(rid)
                all_rows.append(row)

        # 進度條
        fetched = len(all_rows)
        pct = min(100, fetched * 100 // total)
        sys.stdout.write(f"\r    進度：{fetched:,}/{total:,} ({pct}%) [頁 {page}/{total_pages}]")
        sys.stdout.flush()

        page += 1
        time.sleep(REQUEST_DELAY)

    sys.stdout.write("\n")
    return all_rows


def insert_rows(conn: sqlite3.Connection, rows: list[dict], category: str):
    """將下載的資料寫入 SQLite"""
    for row in rows:
        conn.execute("""
            INSERT OR REPLACE INTO tcmb_items
            (id, identifier, index_code, image_license, content_license,
             title, description, original_url, create_dept, last_update_date,
             images, subjects, keywords, tcmb_url, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("id"),
            row.get("identifier", ""),
            row.get("indexCode", ""),
            row.get("imageLicense", ""),
            row.get("contentLicense", ""),
            strip_html(row.get("title", "")),
            strip_html(row.get("description", "")),
            row.get("originalUrl", ""),
            row.get("createDept", ""),
            row.get("lastUpdateDate", ""),
            json.dumps(row.get("images", []), ensure_ascii=False),
            json.dumps(row.get("subjects", []), ensure_ascii=False),
            json.dumps(row.get("keywords", []), ensure_ascii=False),
            row.get("tcmbUrl", ""),
            category,
        ))
    conn.commit()


def rebuild_fts(db_path: Path):
    """重建 FTS5 索引（關閉舊連線 → VACUUM → 全新連線建 FTS）"""
    logger.info("關閉寫入連線，準備重建索引...")

    # Step 1: 用全新連線做 VACUUM（將 WAL 合併回主檔）
    conn = sqlite3.connect(str(db_path))
    item_count = conn.execute("SELECT COUNT(*) FROM tcmb_items").fetchone()[0]
    logger.info(f"資料表 tcmb_items：{item_count:,} 筆")

    logger.info("執行 VACUUM（合併 WAL，重整資料庫）...")
    conn.execute("VACUUM;")
    conn.close()

    # Step 2: VACUUM 後重開，integrity check
    conn = sqlite3.connect(str(db_path))
    result = conn.execute("PRAGMA integrity_check;").fetchone()
    if result[0] != "ok":
        logger.error(f"VACUUM 後仍有完整性問題：{result[0]}")
        conn.close()
        return
    logger.info("資料庫完整性：ok")

    # Step 3: 刪掉舊 FTS 表，從乾淨狀態建立
    conn.execute("DROP TABLE IF EXISTS tcmb_fts;")
    conn.execute("""
        CREATE VIRTUAL TABLE tcmb_fts USING fts5(
            title, description, keywords,
            content='tcmb_items',
            content_rowid='id'
        );
    """)

    logger.info("寫入全文索引...")
    conn.execute("""
        INSERT INTO tcmb_fts(rowid, title, description, keywords)
        SELECT id, title, description, keywords FROM tcmb_items;
    """)
    conn.commit()

    fts_count = conn.execute("SELECT COUNT(*) FROM tcmb_fts").fetchone()[0]
    logger.info(f"全文索引建立完成：{fts_count:,} 筆。")
    conn.close()


# ─────────────────────────────────────────────
# CLI 指令
# ─────────────────────────────────────────────

def _open_db() -> sqlite3.Connection:
    """開啟 DB 連線（含 WAL mode 設定）"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def cmd_build(args):
    """下載指定分類並建立索引"""
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # --build 時刪除舊 DB，從乾淨狀態開始（避免累積 corruption）
    if DB_PATH.exists():
        logger.info(f"刪除舊索引：{DB_PATH}")
        DB_PATH.unlink()
        # 同時清理 WAL/SHM 殘留
        for suffix in ("-wal", "-shm"):
            p = DB_PATH.parent / (DB_PATH.name + suffix)
            if p.exists():
                p.unlink()

    # 初始化 schema
    conn = _open_db()
    init_db(conn)
    conn.close()

    session = requests.Session()
    session.mount("https://tcmbdata.culture.tw", _TcmbSSLAdapter())
    session.headers["User-Agent"] = "TeacherOS-TCMB-Downloader/1.0"

    if args.all:
        subjects = list(CATEGORIES.keys())
    elif args.subjects:
        subjects = args.subjects
    else:
        logger.error("請指定 --all 或 --subjects")
        return

    logger.info(f"目標：{len(subjects)} 個分類")
    total_start = time.time()
    total_records = 0

    for code in subjects:
        if code not in CATEGORIES:
            logger.warning(f"未知分類代碼：{code}，跳過")
            continue

        start = time.time()
        rows = download_category(session, code)
        if rows:
            # 每個分類用獨立連線寫入，避免長時間單一連線導致 corruption
            conn = _open_db()
            insert_rows(conn, rows, code)
            duration = time.time() - start
            conn.execute("""
                INSERT OR REPLACE INTO download_log (category, total_records, downloaded_at, duration_seconds)
                VALUES (?, ?, ?, ?)
            """, (code, len(rows), datetime.now().isoformat(), duration))
            conn.commit()
            conn.close()
            total_records += len(rows)
            logger.info(f"  已寫入 {len(rows):,} 筆，連線已關閉")

    # 驗證寫入結果
    conn = _open_db()
    actual = conn.execute("SELECT COUNT(*) FROM tcmb_items").fetchone()[0]
    conn.close()
    logger.info(f"\n下載完成，tcmb_items 實際筆數：{actual:,}")

    if actual < total_records * 0.9:
        logger.error(f"預期 {total_records:,} 筆但只有 {actual:,} 筆，資料可能損壞")
        return

    rebuild_fts(DB_PATH)

    total_duration = time.time() - total_start
    logger.info(f"\n完成！共 {actual:,} 筆，耗時 {total_duration:.0f} 秒")
    logger.info(f"資料庫位置：{DB_PATH}")


def cmd_update(args):
    """增量更新（重新下載所有已下載的分類）"""
    if not DB_PATH.exists():
        logger.error(f"資料庫不存在：{DB_PATH}，請先執行 --build")
        return

    conn = sqlite3.connect(str(DB_PATH))
    init_db(conn)

    # 讀取已下載的分類
    cursor = conn.execute("SELECT category FROM download_log")
    existing = [row[0] for row in cursor.fetchall()]

    if not existing:
        logger.info("尚無已下載的分類，請先執行 --build")
        conn.close()
        return

    logger.info(f"更新 {len(existing)} 個已下載分類...")

    # 模擬 args 給 cmd_build
    args.subjects = existing
    args.all = False
    conn.close()
    cmd_build(args)


def cmd_status(args):
    """顯示索引狀態"""
    if not DB_PATH.exists():
        logger.info(f"資料庫不存在：{DB_PATH}")
        logger.info("請執行：python3 tcmb_downloader.py --build --all")
        return

    conn = sqlite3.connect(str(DB_PATH))
    logger.info(f"資料庫位置：{DB_PATH}")
    logger.info(f"檔案大小：{DB_PATH.stat().st_size / 1024 / 1024:.1f} MB")

    # 各分類統計
    cursor = conn.execute("""
        SELECT dl.category, dl.total_records, dl.downloaded_at, dl.duration_seconds
        FROM download_log dl ORDER BY dl.total_records DESC
    """)
    rows = cursor.fetchall()
    total = 0
    logger.info(f"\n{'分類':<12} {'筆數':>8} {'下載時間':<20} {'耗時':>6}")
    logger.info("-" * 55)
    for cat, count, at, dur in rows:
        name = CATEGORIES.get(cat, cat)[:10]
        logger.info(f"{name:<12} {count:>8,} {at[:16]:<20} {dur:>5.0f}s")
        total += count
    logger.info("-" * 55)
    logger.info(f"{'合計':<12} {total:>8,}")

    # FTS 統計
    fts_count = conn.execute("SELECT COUNT(*) FROM tcmb_fts").fetchone()[0]
    logger.info(f"\nFTS5 索引：{fts_count:,} 筆")

    conn.close()


def cmd_rebuild_fts(args):
    """單獨重建 FTS 索引（不重新下載）"""
    if not DB_PATH.exists():
        logger.error(f"資料庫不存在：{DB_PATH}")
        return
    rebuild_fts(DB_PATH)


def cmd_search(args):
    """本地全文搜尋測試"""
    if not DB_PATH.exists():
        logger.error(f"資料庫不存在：{DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    query = args.query

    cursor = conn.execute("""
        SELECT i.id, i.title, i.description, i.tcmb_url, i.image_license,
               i.images, i.category, i.keywords
        FROM tcmb_fts f
        JOIN tcmb_items i ON f.rowid = i.id
        WHERE tcmb_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, (query, args.limit))

    rows = cursor.fetchall()
    if not rows:
        logger.info(f"「{query}」無搜尋結果")
        conn.close()
        return

    logger.info(f"「{query}」找到以下結果（顯示前 {args.limit} 筆）：\n")
    for row_id, title, desc, url, img_lic, images_json, cat, kw_json in rows:
        cat_name = CATEGORIES.get(cat, cat)
        desc_short = (desc[:80] + "...") if len(desc) > 80 else desc
        images = json.loads(images_json) if images_json else []
        has_img = "有圖" if images else "無圖"

        logger.info(f"### {title}")
        logger.info(f"  分類：{cat_name} | 圖像：{has_img} ({img_lic}) | ID: {row_id}")
        if desc_short:
            logger.info(f"  描述：{desc_short}")
        if url:
            logger.info(f"  連結：{url}")
        keywords = json.loads(kw_json) if kw_json else []
        if keywords:
            logger.info(f"  關鍵字：{', '.join(keywords[:5])}")
        logger.info("")

    conn.close()


# ─────────────────────────────────────────────
# 主程式
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="國家文化記憶庫本地索引建立器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  python3 tcmb_downloader.py --build --all                    # 下載全部九大分類
  python3 tcmb_downloader.py --build --subjects ART_AND_HUMANITY ETHNIC_AND_LANGUAGE
  python3 tcmb_downloader.py --update                         # 增量更新
  python3 tcmb_downloader.py --status                         # 查看索引狀態
  python3 tcmb_downloader.py --search "達悟族"                # 本地搜尋
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", action="store_true", help="下載並建立索引")
    group.add_argument("--update", action="store_true", help="更新已下載的分類")
    group.add_argument("--status", action="store_true", help="顯示索引狀態")
    group.add_argument("--search", metavar="QUERY", help="本地全文搜尋")
    group.add_argument("--rebuild-fts", action="store_true", help="單獨重建 FTS 索引（不重新下載）")

    parser.add_argument("--all", action="store_true", help="下載全部九大分類")
    parser.add_argument("--subjects", nargs="+", choices=list(CATEGORIES.keys()),
                        help="指定分類代碼", metavar="CODE")
    parser.add_argument("--limit", type=int, default=10, help="搜尋結果數量上限（預設 10）")

    args = parser.parse_args()

    if args.build:
        cmd_build(args)
    elif args.update:
        cmd_update(args)
    elif args.status:
        cmd_status(args)
    elif args.rebuild_fts:
        cmd_rebuild_fts(args)
    elif args.search:
        args.query = args.search
        cmd_search(args)


if __name__ == "__main__":
    main()
