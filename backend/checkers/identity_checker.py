# -*- coding: utf-8 -*-
"""使用集团 qwen2.5-vl-72b 逐页视觉扫描，检测可识别投标人身份的信息。

视觉扫描能发现纯文字提取无法检测的内容：
- 图片型公司 Logo / 印章
- 背景水印
- 图片型签名
"""
import base64
import fitz
from llm_client import get_llm_client
from config import MODEL_VISION

# 页面渲染分辨率，150dpi 在速度和识别率间取得平衡
RENDER_DPI = 150
SCALE = RENDER_DPI / 72

PROMPT = """你是投标文件审查专家。请仔细观察这张页面图片，判断是否存在可以识别投标人身份的内容。

需要识别的内容包括：
1. 公司名称、简称、缩写（含"本公司"等指代）
2. 人员姓名（项目经理、工程师、法人代表等）
3. 公司 Logo、印章、注册商标图案
4. 统一社会信用代码、营业执照号等证件号码
5. 背景水印中包含的公司或个人信息
6. 其他可能暴露投标人身份的任何标记

回答格式：
- 若无上述内容：仅输出"无"
- 若有：逐条列出，格式为"类型：具体内容"，每条占一行

不要输出任何多余解释。"""


def _page_to_base64(page: fitz.Page) -> str:
    mat = fitz.Matrix(SCALE, SCALE)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    return base64.b64encode(pix.tobytes("png")).decode("utf-8")


def check(doc: fitz.Document) -> dict:
    client = get_llm_client()
    all_findings: list[str] = []

    for i, page in enumerate(doc):
        page_num = i + 1
        try:
            img_b64 = _page_to_base64(page)
            resp = client.chat.completions.create(
                model=MODEL_VISION,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                            },
                            {"type": "text", "text": PROMPT},
                        ],
                    }
                ],
                temperature=0,
                max_tokens=512,
            )
            result = resp.choices[0].message.content.strip()
            if result and result != "无":
                for line in result.splitlines():
                    line = line.strip()
                    if line and line != "无":
                        all_findings.append(f"第{page_num}页：{line}")
        except Exception as e:
            all_findings.append(f"第{page_num}页：视觉扫描失败：{e}")

    passed = len(all_findings) == 0
    detail = "未发现可识别身份的信息" if passed else f"发现 {len(all_findings)} 处疑似身份信息"
    return {"passed": passed, "detail": detail, "violations": all_findings}
