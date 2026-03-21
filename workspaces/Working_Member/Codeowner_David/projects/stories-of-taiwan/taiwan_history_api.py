#!/usr/bin/env python3
"""
taiwan_history_api.py — 臺灣主體歷史資料統一介接模組
=====================================================
TeacherOS 備課管線用。將多個臺灣公開歷史資料源包裝成統一的 Python API，
可直接被 Claude Code scheduled task 或 TeacherOS pipeline 呼叫。

資料源清單：
  1. 國家文化記憶庫 2.0 (TCMB) — 臺史博營運，CC 授權文化素材
  2. 國家檔案資訊網 (AA) — 檔管局，含 228/白色恐怖政治檔案
  3. 國家人權博物館 (NHRM) — 不義遺址、政治受難者
  4. 臺灣記憶 (TM) — 國家圖書館，老照片/碑碣/古書契
  5. 政府資料開放平臺 (data.gov.tw) — 結構化歷史資料集
  6. 文化資產國家網路 (BOCH) — 古蹟/歷史建築/文化景觀
  7. 開放博物館 (OpenMuseum) — 中研院，跨館策展

用法：
  from taiwan_history_api import TaiwanHistoryAPI
  api = TaiwanHistoryAPI()
  results = api.search("二二八事件", sources=["tcmb", "archives"])

環境需求：
  pip install requests --break-system-packages

注意事項：
  - TCMB Open API 需事先申請 API Key（至 tcmb.culture.tw/zh-tw/OpenApi 申請）
  - 國家檔案資訊網(AA)目前無正式公開 REST API，本模組透過網頁搜尋介面模擬
  - data.gov.tw 不需 API Key，但有頻率限制
  - 部分資料源可能在維護中暫停服務（BOCH 近期有此情況）

Author: TeacherOS / David
License: MIT
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from urllib.parse import quote, urlencode

try:
    import requests
except ImportError:
    print("請先安裝 requests: pip install requests --break-system-packages")
    raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taiwan_history_api")


# ─────────────────────────────────────────────
# 資料模型
# ─────────────────────────────────────────────

@dataclass
class HistoryItem:
    """統一的歷史素材資料結構"""
    source: str              # 資料來源代碼 (tcmb/archives/nhrm/tm/datagov/boch/openmuseum)
    title: str               # 標題
    description: str = ""    # 描述/摘要
    url: str = ""            # 原始連結
    date: str = ""           # 年代/日期
    location: str = ""       # 相關地點
    category: str = ""       # 分類
    license: str = ""        # 授權方式
    image_url: str = ""      # 圖片連結（如有）
    raw: dict = field(default_factory=dict)  # 原始回傳資料

    def to_dict(self):
        return asdict(self)

    def to_markdown(self) -> str:
        """輸出為 Markdown 格式，方便直接貼入備課文件"""
        lines = [f"### {self.title}"]
        if self.date:
            lines.append(f"**年代**：{self.date}")
        if self.location:
            lines.append(f"**地點**：{self.location}")
        if self.description:
            lines.append(f"\n{self.description[:500]}")
        if self.url:
            lines.append(f"\n[原始連結]({self.url})")
        lines.append(f"\n`來源: {self.source} | 授權: {self.license or '見原站'}`")
        return "\n".join(lines)


# ─────────────────────────────────────────────
# 各資料源適配器
# ─────────────────────────────────────────────

class TCMBAdapter:
    """
    國家文化記憶庫 2.0 (Taiwan Cultural Memory Bank)
    營運：國立臺灣歷史博物館
    Swagger: https://tcmbdata.culture.tw/swagger-ui/
    需申請 API Key: https://tcmb.culture.tw/zh-tw/OpenApi
    """
    BASE = "https://tcmbdata.culture.tw"
    SOURCE = "tcmb"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"

    def search(self, keyword: str, page: int = 1, size: int = 20) -> list[HistoryItem]:
        items = []
        if self.api_key:
            try:
                url = f"{self.BASE}/api/v1/search"
                params = {"keyword": keyword, "page": page, "size": size}
                resp = self.session.get(url, params=params, timeout=15)
                if resp.ok:
                    data = resp.json()
                    for hit in data.get("data", data.get("records", [])):
                        items.append(HistoryItem(
                            source=self.SOURCE,
                            title=hit.get("title", hit.get("name", "")),
                            description=hit.get("description", ""),
                            url=f"https://tcmb.culture.tw/zh-tw/detail?indexCode=online_metadata&id={hit.get('id', '')}",
                            date=hit.get("date", hit.get("createDate", "")),
                            location=hit.get("location", ""),
                            category=hit.get("category", ""),
                            license=hit.get("license", "CC"),
                            image_url=hit.get("imageUrl", ""),
                            raw=hit,
                        ))
                    return items
            except Exception as e:
                logger.warning(f"TCMB API 失敗: {e}")

        # Fallback: 提示手動搜尋
        try:
            search_url = "https://tcmb.culture.tw/zh-tw/datasearch"
            params = {"keyword": keyword}
            logger.info(f"TCMB 無 API Key，請至 {search_url}?{urlencode(params)} 手動搜尋")
            logger.info("或至 https://tcmb.culture.tw/zh-tw/OpenApi 申請 API Key")
        except Exception as e:
            logger.warning(f"TCMB fallback 失敗: {e}")
        return items


class ArchivesAdapter:
    """
    國家檔案資訊網 (AA - Archives Access)
    營運：國家發展委員會檔案管理局
    注意：AA 目前無正式公開 REST API
    """
    SOURCE = "archives"
    AA_SEARCH = "https://aa.archives.gov.tw/archivesData/advanceSearch"
    ART_BASE = "https://art.archives.gov.tw"

    def search(self, keyword: str, political: bool = False) -> list[HistoryItem]:
        items = []
        search_params = {"keyword": keyword}
        if political:
            search_params["isPolitical"] = "true"

        items.append(HistoryItem(
            source=self.SOURCE,
            title=f"國家檔案搜尋：{keyword}",
            description=(
                f"請至國家檔案資訊網搜尋「{keyword}」。"
                f"{'已標記為政治檔案篩選。' if political else ''}"
                f"館藏包含 228 事件、美麗島事件等臺灣民主化檔案，"
                f"以及 1949 年前歷史檔案。數位影像可線上瀏覽。"
            ),
            url=f"{self.AA_SEARCH}?{urlencode(search_params)}",
            category="政治檔案" if political else "國家檔案",
            license="依國家檔案法規定",
        ))

        items.append(HistoryItem(
            source=self.SOURCE,
            title=f"檔案支援教學網：{keyword}",
            description="檔管局專為教學設計的檔案應用資源，含教案與學習單。",
            url=f"{self.ART_BASE}/index.aspx",
            category="教學資源",
            license="教育用途",
        ))
        return items


class NHRMAdapter:
    """
    國家人權博物館 (National Human Rights Museum)
    注意：無正式公開 API，本適配器產生資料庫連結。
    """
    SOURCE = "nhrm"
    BASE = "https://www.nhrm.gov.tw"

    DATABASES = {
        "memory": {
            "name": "國家人權記憶庫",
            "url": "https://hrmtw.nhrm.gov.tw/",
            "desc": "政治受難者口述歷史、影音紀錄",
        },
        "injustice_sites": {
            "name": "不義遺址資料庫",
            "url": "https://hsi.nhrm.gov.tw/",
            "desc": "228 與白色恐怖時期侵害人權發生地，含地理資訊",
        },
        "archives": {
            "name": "檔案史料資訊系統",
            "url": "https://archives.nhrm.gov.tw/",
            "desc": "威權統治時期文物典藏目錄",
        },
        "literature": {
            "name": "白色恐怖文學",
            "url": f"https://www.nhrm.gov.tw/",
            "desc": "以文學作品呈現白色恐怖歷史記憶",
        },
    }

    def search(self, keyword: str, db: str = "all") -> list[HistoryItem]:
        items = []
        targets = self.DATABASES if db == "all" else {db: self.DATABASES.get(db, {})}
        for key, info in targets.items():
            if not info:
                continue
            items.append(HistoryItem(
                source=self.SOURCE,
                title=f"{info['name']}：{keyword}",
                description=info["desc"],
                url=info["url"],
                category="轉型正義",
                license="依人權博物館規定",
            ))
        return items


class TaiwanMemoryAdapter:
    """
    臺灣記憶 Taiwan Memory
    營運：國家圖書館
    無正式 API，本適配器產生搜尋連結。
    """
    SOURCE = "tm"
    BASE = "https://tm.ncl.edu.tw"

    def search(self, keyword: str) -> list[HistoryItem]:
        search_url = f"{self.BASE}/search_result?query_words={quote(keyword)}&page=1&page_limit=20"
        return [HistoryItem(
            source=self.SOURCE,
            title=f"臺灣記憶：{keyword}",
            description=(
                f"國家圖書館數位典藏，含日治時期臺灣明信片、各地老照片、"
                f"舊籍、地方志、古書契、家譜、碑碣拓片、歷史人物小傳等。"
                f"支援地理位置與時間軸檢索。"
            ),
            url=search_url,
            category="數位典藏",
            license="部分開放/部分限館內",
        )]


class DataGovAdapter:
    """
    政府資料開放平臺 (data.gov.tw)
    提供結構化 JSON/CSV 歷史相關資料集，不需 API Key。
    """
    SOURCE = "datagov"
    BASE = "https://data.gov.tw/api/v2"

    KNOWN_DATASETS = {
        "228_monuments": {"id": "6270", "name": "二二八事件紀念碑(物)資料"},
        "cultural_heritage": {"id": "6242", "name": "文化資產-古蹟"},
        "historical_buildings": {"id": "6243", "name": "文化資產-歷史建築"},
        "cultural_landscape": {"id": "6244", "name": "文化資產-文化景觀"},
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "TeacherOS/1.0"

    def search(self, keyword: str, limit: int = 20) -> list[HistoryItem]:
        items = []
        try:
            url = f"{self.BASE}/datasets"
            params = {"q": keyword, "limit": limit, "format": "json"}
            resp = self.session.get(url, params=params, timeout=15)
            if resp.ok:
                data = resp.json()
                for ds in data.get("data", data.get("result", {}).get("results", [])):
                    ds_id = ds.get("id", ds.get("datasetId", ""))
                    items.append(HistoryItem(
                        source=self.SOURCE,
                        title=ds.get("title", ds.get("name", "")),
                        description=ds.get("description", ds.get("notes", ""))[:300],
                        url=f"https://data.gov.tw/dataset/{ds_id}",
                        category=ds.get("categoryName", ""),
                        license=ds.get("license", "政府資料開放授權"),
                        raw=ds,
                    ))
        except Exception as e:
            logger.warning(f"data.gov.tw 搜尋失敗: {e}")
        return items

    def fetch_dataset(self, dataset_id: str, limit: int = 100) -> list[dict]:
        try:
            url = f"{self.BASE}/datasets/{dataset_id}/data"
            params = {"limit": limit, "format": "json"}
            resp = self.session.get(url, params=params, timeout=15)
            if resp.ok:
                data = resp.json()
                return data.get("data", data.get("result", {}).get("records", []))
        except Exception as e:
            logger.warning(f"data.gov.tw 資料集 {dataset_id} 取得失敗: {e}")
        return []


class BOCHAdapter:
    """
    文化資產國家網路 (Bureau of Cultural Heritage)
    注意：近期有維護停機情況，API 端點可能已遷移。
    """
    SOURCE = "boch"
    BASE = "https://data.boch.gov.tw/opendata/v2"

    def __init__(self):
        self.session = requests.Session()

    def search(self, keyword: str = "", category: str = "monument", limit: int = 20) -> list[HistoryItem]:
        items = []
        try:
            url = f"{self.BASE}/{category}"
            params = {"keyword": keyword, "pageSize": limit} if keyword else {"pageSize": limit}
            resp = self.session.get(url, params=params, timeout=15)
            if resp.ok:
                data = resp.json()
                records = data if isinstance(data, list) else data.get("data", [])
                for rec in records:
                    items.append(HistoryItem(
                        source=self.SOURCE,
                        title=rec.get("name", rec.get("caseName", "")),
                        description=rec.get("summary", rec.get("briefIntroduction", ""))[:300],
                        url=rec.get("webUrl", ""),
                        date=rec.get("registerDate", rec.get("publicNoticeDate", "")),
                        location=rec.get("cityName", "") + rec.get("areaName", ""),
                        category=category,
                        license="政府資料開放授權",
                        raw=rec,
                    ))
        except Exception as e:
            logger.warning(f"BOCH API 失敗（可能維護中）: {e}")
        return items


class OpenMuseumAdapter:
    """
    開放博物館 (OpenMuseum)
    營運：中央研究院數位文化中心
    無正式 API，產生搜尋連結。
    """
    SOURCE = "openmuseum"
    BASE = "https://openmuseum.tw"

    def search(self, keyword: str) -> list[HistoryItem]:
        return [HistoryItem(
            source=self.SOURCE,
            title=f"開放博物館：{keyword}",
            description="中研院跨館策展平台，含國家人權博物館、臺史博等館藏。",
            url=f"{self.BASE}/search?q={quote(keyword)}",
            category="跨館策展",
            license="依各館規定",
        )]


# ─────────────────────────────────────────────
# 統一 API 入口
# ─────────────────────────────────────────────

class TaiwanHistoryAPI:
    """臺灣主體歷史資料統一搜尋 API"""

    ALL_SOURCES = ["tcmb", "archives", "nhrm", "tm", "datagov", "boch", "openmuseum"]

    def __init__(self, tcmb_api_key: str = ""):
        self.adapters = {
            "tcmb": TCMBAdapter(api_key=tcmb_api_key),
            "archives": ArchivesAdapter(),
            "nhrm": NHRMAdapter(),
            "tm": TaiwanMemoryAdapter(),
            "datagov": DataGovAdapter(),
            "boch": BOCHAdapter(),
            "openmuseum": OpenMuseumAdapter(),
        }

    def search(
        self,
        keyword: str,
        sources: Optional[list[str]] = None,
        political: bool = False,
    ) -> list[HistoryItem]:
        sources = sources or self.ALL_SOURCES
        all_items = []
        for src in sources:
            adapter = self.adapters.get(src)
            if not adapter:
                logger.warning(f"未知來源: {src}")
                continue
            try:
                if src == "archives":
                    items = adapter.search(keyword, political=political)
                else:
                    items = adapter.search(keyword)
                all_items.extend(items)
                time.sleep(0.3)
            except Exception as e:
                logger.error(f"搜尋 {src} 失敗: {e}")
        return all_items

    def search_political_archives(self, keyword: str) -> list[HistoryItem]:
        return self.search(keyword, sources=["archives", "nhrm", "tcmb", "openmuseum"], political=True)

    def search_cultural_heritage(self, keyword: str) -> list[HistoryItem]:
        items = []
        boch = self.adapters["boch"]
        for cat in ["monument", "historicBuilding", "culturalLandscape", "archaeologicalSite"]:
            items.extend(boch.search(keyword=keyword, category=cat, limit=10))
            time.sleep(0.3)
        return items

    def search_for_lesson(self, topic: str, grade: int = 9, era: str = "") -> dict:
        keyword = f"{era} {topic}".strip() if era else topic
        result = {
            "topic": topic, "grade": grade, "era": era,
            "primary_sources": [], "teaching_resources": [],
            "cultural_sites": [], "visual_materials": [], "references": [],
        }
        result["primary_sources"] = self.search(keyword, sources=["archives", "nhrm"])
        result["teaching_resources"] = self.search(keyword, sources=["openmuseum"])
        result["cultural_sites"] = self.search_cultural_heritage(keyword)
        result["visual_materials"] = self.search(keyword, sources=["tm", "tcmb"])
        result["references"] = self.search(keyword, sources=["datagov"])
        return result

    # ─── 輸出格式 ───

    @staticmethod
    def to_markdown(items: list[HistoryItem], title: str = "") -> str:
        lines = []
        if title:
            lines.append(f"# {title}\n")
        by_source = {}
        for item in items:
            by_source.setdefault(item.source, []).append(item)
        source_names = {
            "tcmb": "國家文化記憶庫", "archives": "國家檔案",
            "nhrm": "國家人權博物館", "tm": "臺灣記憶",
            "datagov": "政府開放資料", "boch": "文化資產",
            "openmuseum": "開放博物館",
        }
        for src, src_items in by_source.items():
            lines.append(f"\n## {source_names.get(src, src)}\n")
            for item in src_items:
                lines.append(item.to_markdown())
                lines.append("")
        return "\n".join(lines)

    @staticmethod
    def to_json(items: list[HistoryItem]) -> str:
        return json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)

    @staticmethod
    def to_lesson_markdown(lesson_data: dict) -> str:
        lines = [
            f"# 備課素材：{lesson_data['topic']}",
            f"**年級**：{lesson_data['grade']} | **年代**：{lesson_data.get('era', '不限')}",
            "",
        ]
        section_names = {
            "primary_sources": "一手史料", "teaching_resources": "教學資源",
            "cultural_sites": "文化資產/遺址", "visual_materials": "圖像/影音素材",
            "references": "參考資料",
        }
        for key, name in section_names.items():
            items = lesson_data.get(key, [])
            lines.append(f"\n## {name} ({len(items)} 筆)\n")
            if not items:
                lines.append("（無結果）\n")
            for item in items:
                lines.append(item.to_markdown())
                lines.append("")
        return "\n".join(lines)


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="臺灣主體歷史資料統一搜尋 CLI")
    parser.add_argument("keyword", help="搜尋關鍵字")
    parser.add_argument("--sources", "-s", nargs="+", choices=TaiwanHistoryAPI.ALL_SOURCES)
    parser.add_argument("--political", "-p", action="store_true")
    parser.add_argument("--lesson", "-l", action="store_true")
    parser.add_argument("--grade", "-g", type=int, default=9)
    parser.add_argument("--era", "-e", default="")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--tcmb-key", default="")
    parser.add_argument("--output", "-o", default="")
    args = parser.parse_args()

    api = TaiwanHistoryAPI(tcmb_api_key=args.tcmb_key)

    if args.lesson:
        data = api.search_for_lesson(topic=args.keyword, grade=args.grade, era=args.era)
        output = api.to_lesson_markdown(data)
    else:
        results = api.search(args.keyword, sources=args.sources, political=args.political)
        output = api.to_json(results) if args.format == "json" else api.to_markdown(results, title=f"搜尋：{args.keyword}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已寫入 {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
