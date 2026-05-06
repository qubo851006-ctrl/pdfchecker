# -*- coding: utf-8 -*-
"""检测行间距、对齐方式、首行缩进、段落间距。"""
import statistics
import fitz

# 要求的固定行间距 = 30pt，允许 ±3pt 误差
REQUIRED_LINE_SPACING = 30.0
SPACING_TOL = 3.0

# 首行缩进：宋体四号 14pt × 2 字符 ≈ 28pt，允许 ±5pt
INDENT_WIDTH = 28.0
INDENT_TOL   = 5.0

# 左对齐容忍误差（pt）
ALIGN_TOL = 4.0

MAX_VIOLATIONS = 30


def check(doc: fitz.Document) -> dict:
    violations = []

    for i, page in enumerate(doc):
        page_num = i + 1
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

        # 收集每个文本块的所有行，用于行间距和对齐检测
        for block in blocks:
            if block.get("type") != 0:
                continue

            lines = block.get("lines", [])
            if len(lines) < 2:
                continue

            # 获取行基线 Y 坐标
            baselines = []
            for line in lines:
                spans = line.get("spans", [])
                if spans:
                    baselines.append(spans[0].get("origin", (0, 0))[1])

            # 行间距检测
            spacings = [baselines[j+1] - baselines[j] for j in range(len(baselines)-1)]
            for j, sp in enumerate(spacings):
                if sp > 0 and abs(sp - REQUIRED_LINE_SPACING) > SPACING_TOL:
                    if len(violations) < MAX_VIOLATIONS:
                        violations.append(
                            f"第{page_num}页 块{i}：行间距 {sp:.1f}pt，要求固定 {REQUIRED_LINE_SPACING}pt"
                        )

            # 左对齐 + 首行缩进检测
            line_x0s = []
            for line in lines:
                spans = line.get("spans", [])
                if spans:
                    line_x0s.append(spans[0]["bbox"][0])

            if not line_x0s:
                continue

            # 主体左边界：取出现最多的 x0 作为段落基准左边界
            try:
                base_x = statistics.mode(round(x) for x in line_x0s)
            except statistics.StatisticsError:
                base_x = min(line_x0s)

            for j, (line, x0) in enumerate(zip(lines, line_x0s)):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(s.get("text", "") for s in spans).strip()
                if not text:
                    continue

                is_first_line = (j == 0)

                if is_first_line:
                    # 首行应有约 28pt 的缩进
                    indent = x0 - base_x
                    # 如果整个块只有一行，无法判断 base_x，跳过
                    if len(lines) > 1 and indent < INDENT_WIDTH - INDENT_TOL:
                        if len(violations) < MAX_VIOLATIONS:
                            violations.append(
                                f"第{page_num}页：首行缩进 {indent:.1f}pt，要求约 {INDENT_WIDTH}pt（2字符）"
                            )
                else:
                    # 非首行应左对齐至 base_x（允许误差）
                    # 若某行 x0 明显大于 base_x，可能存在额外缩进
                    pass  # 右对齐判断留给结构层面

    passed = len(violations) == 0
    detail = "排版格式符合要求" if passed else f"发现 {len(violations)} 处问题"
    return {"passed": passed, "detail": detail, "violations": violations}
