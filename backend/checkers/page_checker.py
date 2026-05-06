# -*- coding: utf-8 -*-
"""检测页面尺寸和页边距。"""
import fitz

# A4 尺寸（单位：点）
A4_WIDTH  = 595.28
A4_HEIGHT = 841.89
SIZE_TOL  = 2.0  # 允许误差 ±2pt

# 页边距（单位：点，1cm = 28.3465pt）
CM = 28.3465
MARGIN_TOP   = 2.5 * CM   # 70.87pt
MARGIN_OTHER = 2.0 * CM   # 56.69pt
MARGIN_TOL   = 4.0        # 允许误差 ±4pt


def check(doc: fitz.Document) -> dict:
    violations = []

    for i, page in enumerate(doc):
        page_num = i + 1
        rect = page.rect

        # 检查 A4 尺寸
        if abs(rect.width - A4_WIDTH) > SIZE_TOL or abs(rect.height - A4_HEIGHT) > SIZE_TOL:
            violations.append(
                f"第{page_num}页：页面尺寸 {rect.width:.1f}×{rect.height:.1f}pt，"
                f"非 A4（{A4_WIDTH}×{A4_HEIGHT}pt）"
            )

        # 通过文本块位置推断实际页边距
        blocks = page.get_text("blocks")
        if not blocks:
            continue

        xs = [b[0] for b in blocks]
        ys = [b[1] for b in blocks]
        x2s = [b[2] for b in blocks]
        y2s = [b[3] for b in blocks]

        actual_top    = min(ys)
        actual_left   = min(xs)
        actual_right  = rect.width - max(x2s)
        actual_bottom = rect.height - max(y2s)

        expected_left   = MARGIN_OTHER
        expected_right  = MARGIN_OTHER
        expected_top    = MARGIN_TOP
        expected_bottom = MARGIN_OTHER

        if actual_top < expected_top - MARGIN_TOL:
            violations.append(
                f"第{page_num}页：上边距约 {actual_top / CM:.2f}cm，要求 2.5cm"
            )
        if actual_left < expected_left - MARGIN_TOL:
            violations.append(
                f"第{page_num}页：左边距约 {actual_left / CM:.2f}cm，要求 2cm"
            )
        if actual_right < expected_right - MARGIN_TOL:
            violations.append(
                f"第{page_num}页：右边距约 {actual_right / CM:.2f}cm，要求 2cm"
            )
        if actual_bottom < expected_bottom - MARGIN_TOL:
            violations.append(
                f"第{page_num}页：下边距约 {actual_bottom / CM:.2f}cm，要求 2cm"
            )

    passed = len(violations) == 0
    detail = "页面尺寸和页边距符合要求" if passed else f"发现 {len(violations)} 处问题"
    return {"passed": passed, "detail": detail, "violations": violations}
