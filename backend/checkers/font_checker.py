# -*- coding: utf-8 -*-
"""检测字体、字号、颜色、加粗、斜体、下划线。"""
import fitz

# 四号字 = 14pt；允许 ±0.5pt 误差（PDF 渲染可能有微小偏差）
REQUIRED_SIZE = 14.0
SIZE_TOL = 0.8

# 宋体在 PDF 中常见嵌入名称
SONGTI_NAMES = {"simsun", "宋体", "songti", "stsong", "fzsong"}

# fitz span flags 位掩码
FLAG_ITALIC = 1 << 1   # bit1
FLAG_BOLD   = 1 << 4   # bit4

# 最多汇报的违规条数，避免输出过多
MAX_VIOLATIONS = 30


def _strip_subset(font_name: str) -> str:
    """去掉 PDF 子集前缀，如 ABCDEF+SimSun → SimSun"""
    if "+" in font_name:
        return font_name.split("+", 1)[1]
    return font_name


def _is_songti(font_name: str) -> bool:
    name = _strip_subset(font_name).lower()
    return any(s in name for s in SONGTI_NAMES)


def check(doc: fitz.Document) -> dict:
    violations = []

    for i, page in enumerate(doc):
        page_num = i + 1
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

        for block in blocks:
            if block.get("type") != 0:  # 只处理文本块
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue

                    font_name = span.get("font", "")
                    size      = span.get("size", 0)
                    color     = span.get("color", 0)
                    flags     = span.get("flags", 0)
                    origin_y  = span.get("origin", (0, 0))[1]
                    loc       = f"第{page_num}页 约第{int(origin_y)}pt行"

                    # 字体检查
                    if not _is_songti(font_name):
                        if len(violations) < MAX_VIOLATIONS:
                            violations.append(
                                f"{loc}：字体[{font_name}]非宋体，内容：{text[:20]}"
                            )

                    # 字号检查
                    if abs(size - REQUIRED_SIZE) > SIZE_TOL:
                        if len(violations) < MAX_VIOLATIONS:
                            violations.append(
                                f"{loc}：字号 {size:.1f}pt（四号应为 {REQUIRED_SIZE}pt），内容：{text[:20]}"
                            )

                    # 颜色检查（黑色 = 0x000000 = 0）
                    if color != 0:
                        r = (color >> 16) & 0xFF
                        g = (color >> 8)  & 0xFF
                        b = color & 0xFF
                        if len(violations) < MAX_VIOLATIONS:
                            violations.append(
                                f"{loc}：文字颜色 RGB({r},{g},{b}) 非黑色，内容：{text[:20]}"
                            )

                    # 加粗检查
                    bold_by_flag = bool(flags & FLAG_BOLD)
                    bold_by_name = "bold" in font_name.lower()
                    if bold_by_flag or bold_by_name:
                        if len(violations) < MAX_VIOLATIONS:
                            violations.append(
                                f"{loc}：文字加粗，内容：{text[:20]}"
                            )

                    # 斜体检查
                    italic_by_flag = bool(flags & FLAG_ITALIC)
                    italic_by_name = "italic" in font_name.lower() or "oblique" in font_name.lower()
                    if italic_by_flag or italic_by_name:
                        if len(violations) < MAX_VIOLATIONS:
                            violations.append(
                                f"{loc}：文字斜体，内容：{text[:20]}"
                            )

    # 下划线通过绘图路径检测（Word 转 PDF 的下划线是独立的线段）
    for i, page in enumerate(doc):
        page_num = i + 1
        paths = page.get_drawings()
        text_rects = [
            span["bbox"]
            for block in page.get_text("dict")["blocks"]
            if block.get("type") == 0
            for line in block.get("lines", [])
            for span in line.get("spans", [])
        ]
        for path in paths:
            if path.get("type") != "l":  # 只看直线
                continue
            rect = path.get("rect", fitz.Rect())
            # 下划线特征：极细水平线
            if rect.height > 2:
                continue
            # 检查该线是否在某行文字正下方
            for tr in text_rects:
                tx0, ty0, tx1, ty1 = tr
                if rect.y0 >= ty0 and rect.y0 <= ty1 + 4 and rect.x0 >= tx0 - 2 and rect.x1 <= tx1 + 2:
                    if len(violations) < MAX_VIOLATIONS:
                        violations.append(
                            f"第{page_num}页：检测到下划线（y≈{rect.y0:.0f}pt）"
                        )
                    break

    passed = len(violations) == 0
    detail = "字体格式符合要求" if passed else f"发现 {len(violations)} 处问题"
    return {"passed": passed, "detail": detail, "violations": violations}
