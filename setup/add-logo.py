#!/usr/bin/env python3
# TeacherOS — 識別 Logo 後處理腳本
# 用途：
#   1. 精準偵測圓形邊界，去除白色背景，只保留圓形 Logo
#   2. 壓縮至適合標題行使用的尺寸
#   3. 用無框雙欄表格排版：左欄標題文字、右欄 Logo 垂直置中
#
# 呼叫方式（由 build.sh 自動執行）：
#   python3 setup/add-logo.py <docx路徑>

import sys
from pathlib import Path
from collections import deque

try:
    from docx import Document
    from docx.shared import Cm, Twips
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    print("錯誤：缺少 python-docx 套件。請執行：pip3 install python-docx")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw
    import numpy as np
    import io
except ImportError:
    print("錯誤：缺少 Pillow 或 numpy 套件。請執行：pip3 install Pillow numpy")
    sys.exit(1)

REPO_ROOT   = Path(__file__).parent.parent
LOGO_SRC    = REPO_ROOT / "setup" / "assets" / "logo.png"
LOGO_READY  = REPO_ROOT / "setup" / "assets" / "logo-ready.png"

LOGO_SIZE_PX    = 300   # 最終圓形 Logo 解析度（px）
LOGO_DEFAULT_PT = 22    # 字體大小預設值（pt）


def flood_fill_background(arr_gray, tolerance=30):
    """
    從四個角落進行 BFS flood fill，偵測白色背景區域。
    回傳 bool mask：True = 背景（要去除），False = 圓形內容（要保留）
    """
    h, w = arr_gray.shape
    visited = np.zeros((h, w), dtype=bool)
    is_background = np.zeros((h, w), dtype=bool)
    queue = deque()

    seeds = [(0, 0), (0, w-1), (h-1, 0), (h-1, w-1)]
    for r, c in seeds:
        if arr_gray[r, c] > (255 - tolerance):
            queue.append((r, c))
            visited[r, c] = True

    while queue:
        r, c = queue.popleft()
        is_background[r, c] = True
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < h and 0 <= nc < w and not visited[nr, nc]:
                if arr_gray[nr, nc] > (255 - tolerance):
                    visited[nr, nc] = True
                    queue.append((nr, nc))

    return is_background


def prepare_logo():
    """
    精準去背：
    1. BFS 從角落填充白色背景 → 設為透明
    2. 裁切成正方形並縮放
    3. 套用精確圓形遮罩（確保邊緣乾淨）
    4. 輸出壓縮後的 logo-ready.png
    """
    img = Image.open(LOGO_SRC).convert("RGBA")
    arr = np.array(img)

    gray = np.array(img.convert("L"))
    bg_mask = flood_fill_background(gray, tolerance=25)
    arr[bg_mask, 3] = 0
    img = Image.fromarray(arr)

    alpha = np.array(img.split()[3])
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    img = img.crop((cmin, rmin, cmax+1, rmax+1))

    side = max(img.width, img.height)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ox = (side - img.width)  // 2
    oy = (side - img.height) // 2
    square.paste(img, (ox, oy), mask=img)
    square = square.resize((LOGO_SIZE_PX, LOGO_SIZE_PX), Image.LANCZOS)

    inset = 3
    circle_mask = Image.new("L", (LOGO_SIZE_PX, LOGO_SIZE_PX), 0)
    draw = ImageDraw.Draw(circle_mask)
    draw.ellipse(
        (inset, inset, LOGO_SIZE_PX - inset - 1, LOGO_SIZE_PX - inset - 1),
        fill=255
    )
    r, g, b, a = square.split()
    final_alpha = Image.fromarray(
        np.minimum(np.array(a), np.array(circle_mask)).astype("uint8")
    )
    result = Image.merge("RGBA", (r, g, b, final_alpha))
    result.save(LOGO_READY, "PNG", optimize=True)

    size_kb = LOGO_READY.stat().st_size // 1024
    arr_check = np.array(result)
    corner_alpha_max = max(
        arr_check[:5,  :5,  3].max(),
        arr_check[:5,  -5:, 3].max(),
        arr_check[-5:, :5,  3].max(),
        arr_check[-5:, -5:, 3].max(),
    )
    print(f"Logo 處理完成：{size_kb}KB（圓形精準去背，四角 alpha={corner_alpha_max}）")
    return LOGO_READY


def logo_to_bytes(logo_path):
    buf = io.BytesIO()
    with Image.open(logo_path) as img:
        img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def detect_font_pt(para):
    """從段落 run 與樣式鏈取得字體大小（pt）。"""
    pt = None
    for run in para.runs:
        if run.font.size:
            pt = run.font.size.pt
            break
    if pt is None:
        style = para.style
        while style and pt is None:
            if style.font.size:
                pt = style.font.size.pt
            style = style.base_style
    return pt or LOGO_DEFAULT_PT


def clear_header(doc):
    """清除所有 section 的頁首內容"""
    for section in doc.sections:
        header = section.header
        header.is_linked_to_previous = False
        for para in header.paragraphs:
            para.clear()


def _get_or_create_child(parent, tag):
    """在 parent 下取得或新建指定 tag 的第一個子元素"""
    el = parent.find(qn(tag))
    if el is None:
        el = OxmlElement(tag)
        parent.insert(0, el)
    return el


def _set_no_borders(pr_el, sides, borders_tag):
    """在 tblPr 或 tcPr 中，將指定框線設為 none"""
    for existing in pr_el.findall(qn(borders_tag)):
        pr_el.remove(existing)
    borders_el = OxmlElement(borders_tag)
    for side in sides:
        el = OxmlElement(side)
        el.set(qn('w:val'), 'none')
        el.set(qn('w:sz'), '0')
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), 'auto')
        borders_el.append(el)
    pr_el.append(borders_el)


def remove_all_borders(table):
    """移除表格及所有儲存格的框線"""
    tbl   = table._tbl
    tblPr = _get_or_create_child(tbl, 'w:tblPr')
    _set_no_borders(tblPr,
        ['w:top','w:left','w:bottom','w:right','w:insideH','w:insideV'],
        'w:tblBorders')

    for row in table.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            _set_no_borders(tcPr,
                ['w:top','w:left','w:bottom','w:right'],
                'w:tcBorders')


def set_cell_margins_zero(cell):
    """清除儲存格內距"""
    tcPr = cell._tc.get_or_add_tcPr()
    for existing in tcPr.findall(qn('w:tcMar')):
        tcPr.remove(existing)
    tcMar = OxmlElement('w:tcMar')
    for side in ['w:top', 'w:start', 'w:bottom', 'w:end']:
        el = OxmlElement(side)
        el.set(qn('w:w'), '0')
        el.set(qn('w:type'), 'dxa')
        tcMar.append(el)
    tcPr.append(tcMar)


def set_cell_width(cell, width_twips):
    """設定儲存格寬度（twips）"""
    tcPr = cell._tc.get_or_add_tcPr()
    for existing in tcPr.findall(qn('w:tcW')):
        tcPr.remove(existing)
    tcW = OxmlElement('w:tcW')
    tcW.set(qn('w:w'), str(width_twips))
    tcW.set(qn('w:type'), 'dxa')
    tcPr.append(tcW)


def add_logo_table_layout(docx_path: str, logo_path: Path):
    """
    以無框雙欄表格排版標題行：

      ┌─────────────────────────────┬──────┐
      │  9C 春季班親會通知（Heading 1） │  ●   │  ← Logo 垂直置中
      └─────────────────────────────┴──────┘

    技術說明：
      - w:position 對 inline drawing 無效，只能作用於文字 run
      - 唯一可靠的垂直置中方式是 table cell 的 w:vAlign
      - 表格設為無框線、無內距，視覺上與普通標題段落相同
    """
    doc = Document(docx_path)
    clear_header(doc)

    # 找第一個非空段落（標題）
    title_para = None
    for para in doc.paragraphs:
        if para.text.strip():
            title_para = para
            break

    if title_para is None:
        print("警告：找不到標題段落，略過 Logo 嵌入。")
        doc.save(docx_path)
        return

    font_pt   = detect_font_pt(title_para)
    logo_h_cm = max(font_pt * 0.06, 1.2)

    # 計算欄寬（twips，1cm = 567 twips）
    section     = doc.sections[0]
    page_w      = section.page_width.twips  if section.page_width  else 11906
    left_m      = section.left_margin.twips if section.left_margin else 1800
    right_m     = section.right_margin.twips if section.right_margin else 1800
    text_w      = page_w - left_m - right_m
    logo_col_w  = int((logo_h_cm + 0.4) * 567)   # Logo 直徑 + 左右各 0.2cm
    title_col_w = text_w - logo_col_w

    # 在標題段落之前插入表格
    body     = title_para._p.getparent()
    title_p  = title_para._p
    title_idx = list(body).index(title_p)

    table = doc.add_table(rows=1, cols=2)
    tbl   = table._tbl
    body.remove(tbl)                    # add_table 會 append 到最後，先取出
    body.insert(title_idx, tbl)         # 插入到標題原本的位置

    # 表格屬性：固定寬度、全文字寬
    tblPr = _get_or_create_child(tbl, 'w:tblPr')

    # 移除任何繼承樣式（避免帶入框線）
    for el in tblPr.findall(qn('w:tblStyle')):
        tblPr.remove(el)
    tblW  = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), str(text_w))
    tblW.set(qn('w:type'), 'dxa')
    tblPr.append(tblW)
    tblLayout = OxmlElement('w:tblLayout')
    tblLayout.set(qn('w:type'), 'fixed')
    tblPr.append(tblLayout)

    # 移除所有框線
    remove_all_borders(table)

    left_cell  = table.rows[0].cells[0]
    right_cell = table.rows[0].cells[1]

    # 設定欄寬與零內距
    set_cell_width(left_cell,  title_col_w)
    set_cell_width(right_cell, logo_col_w)
    set_cell_margins_zero(left_cell)
    set_cell_margins_zero(right_cell)

    # 左欄：標題文字（保留原始樣式與 run 格式）
    left_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    left_para = left_cell.paragraphs[0]
    left_para.style = title_para.style
    for run in title_para.runs:
        new_run = left_para.add_run(run.text)
        new_run.bold   = run.bold
        new_run.italic = run.italic
        if run.font.name:
            new_run.font.name = run.font.name
        if run.font.size:
            new_run.font.size = run.font.size
        try:
            if run.font.color.type:
                new_run.font.color.rgb = run.font.color.rgb
        except Exception:
            pass
    # 若無 runs（純文字段落），直接設定文字
    if not title_para.runs:
        left_para.add_run(title_para.text)

    # 右欄：Logo，垂直置中 + 水平置中
    right_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    right_para = right_cell.paragraphs[0]
    right_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    logo_run = right_para.add_run()
    logo_run.add_picture(logo_to_bytes(logo_path), height=Cm(logo_h_cm))

    # 移除原始標題段落
    body.remove(title_p)

    doc.save(docx_path)
    print(
        f"Logo 已嵌入標題右側（高度 {logo_h_cm:.2f}cm，無框表格排版，垂直置中）："
        f"{Path(docx_path).name}"
    )


def main():
    if len(sys.argv) < 2:
        print("用法：python3 setup/add-logo.py <docx路徑>")
        sys.exit(1)

    docx_path = sys.argv[1]

    if not Path(docx_path).exists():
        print(f"錯誤：找不到檔案 {docx_path}")
        sys.exit(1)

    if not LOGO_SRC.exists():
        print(f"警告：找不到 Logo 原始檔（{LOGO_SRC}），略過。")
        return

    logo_ready = prepare_logo()
    add_logo_table_layout(docx_path, logo_ready)


if __name__ == "__main__":
    main()
