# -*- coding: utf-8 -*-
"""检测封面、目录、页眉、页脚、页码。"""
import re
import fitz

CM = 28.3465
# 页眉区：页面顶部 60pt 以内
HEADER_ZONE = 60.0
# 页脚区：页面底部 60pt 以内
FOOTER_ZONE = 60.0

# 目录特征：引导符（……）或连续点+数字
TOC_LEADER_RE = re.compile(r"[.…·]{3,}\s*\d+\s*$")
TOC_HEADING_RE = re.compile(r"目\s*录")

# 页码特征：仅含数字或"第X页"
PAGE_NUM_RE = re.compile(r"^\s*(\d+|第\s*\d+\s*页)\s*$")

MAX_VIOLATIONS = 20


def _get_text_in_zone(page: fitz.Page, zone_y_min: float, zone_y_max: float) -> list[str]:
    texts = []
    for block in page.get_text("blocks"):
        bx0, by0, bx1, by1, text, *_ = block
        if by0 >= zone_y_min and by1 <= zone_y_max:
            t = text.strip()
            if t:
                texts.append(t)
    return texts


def check(doc: fitz.Document) -> dict:
    violations = []
    total_pages = len(doc)

    # 检测封面：第一页文字极少或有典型封面特征（大字标题居中，无正文段落）
    if total_pages > 0:
        first_page = doc[0]
        first_blocks = [b for b in first_page.get_text("blocks") if b[4].strip()]
        if len(first_blocks) <= 3:
            # 文字极少，疑似封面
            texts = [b[4].strip() for b in first_blocks]
            joined = " ".join(texts)
            if len(joined) < 100:
                violations.append(f"第1页：疑似封面（文字极少），暗标不得有封面")

    # 检测目录
    for i, page in enumerate(doc):
        page_num = i + 1
        full_text = page.get_text()
        if TOC_HEADING_RE.search(full_text):
            violations.append(f"第{page_num}页：发现[目录]字样，暗标不得有目录")
        # 检测引导符（目录条目特征）
        for line in full_text.splitlines():
            if TOC_LEADER_RE.search(line):
                violations.append(
                    f"第{page_num}页：发现目录引导符格式（…+页码），疑似目录条目：{line.strip()[:40]}"
                )
                break  # 每页只报一次

    # 检测页眉（每页顶部区域）
    header_texts_by_page: dict[int, list[str]] = {}
    for i, page in enumerate(doc):
        page_height = page.rect.height
        texts = _get_text_in_zone(page, 0, HEADER_ZONE)
        if texts:
            header_texts_by_page[i + 1] = texts

    if header_texts_by_page:
        pages_with_header = sorted(header_texts_by_page.keys())
        sample = header_texts_by_page[pages_with_header[0]]
        violations.append(
            f"第{pages_with_header[0]}页等 {len(pages_with_header)} 页顶部区域有文字，疑似页眉：[{sample[0][:30]}]"
        )

    # 检测页脚和页码（每页底部区域）
    footer_pages = []
    page_num_pages = []
    for i, page in enumerate(doc):
        page_height = page.rect.height
        texts = _get_text_in_zone(page, page_height - FOOTER_ZONE, page_height)
        if texts:
            for t in texts:
                if PAGE_NUM_RE.match(t):
                    page_num_pages.append(i + 1)
                else:
                    footer_pages.append(i + 1)

    if page_num_pages:
        violations.append(
            f"第{page_num_pages[0]}页等 {len(page_num_pages)} 页发现页码"
        )
    if footer_pages:
        violations.append(
            f"第{footer_pages[0]}页等 {len(footer_pages)} 页底部区域有文字，疑似页脚"
        )

    passed = len(violations) == 0
    detail = "文档结构符合要求（无封面/目录/页眉/页脚/页码）" if passed else f"发现 {len(violations)} 处问题"
    return {"passed": passed, "detail": detail, "violations": violations}
