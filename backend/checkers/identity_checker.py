# -*- coding: utf-8 -*-
"""使用 LLM 扫描文本，检测可识别投标人身份的信息。"""
import fitz
from llm_client import get_llm_client
from config import MODEL_CHAT

# 每次发给 LLM 的最大字符数（避免 token 超限）
CHUNK_SIZE = 3000

SYSTEM_PROMPT = """你是一个投标文件审查专家。你的任务是检查文字内容中是否出现了可以识别投标人身份的信息。

需要识别的内容包括：
1. 公司名称（含简称、缩写，如"XX公司"、"本公司"指代性表述）
2. 人员姓名（项目经理、工程师、法人等）
3. 注册商标、品牌标识的文字描述
4. 统一社会信用代码、营业执照号等证件号码
5. 其他可能暴露投标人身份的特定标记

请用以下格式回答：
- 若无上述内容：仅输出"无"
- 若有：逐条列出，格式为"类型：原文内容"，每条占一行

不要输出任何多余解释。"""


def _extract_text_chunks(doc: fitz.Document) -> list[str]:
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"

    chunks = []
    for i in range(0, len(full_text), CHUNK_SIZE):
        chunk = full_text[i:i + CHUNK_SIZE].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def check(doc: fitz.Document) -> dict:
    chunks = _extract_text_chunks(doc)
    if not chunks:
        return {"passed": True, "detail": "文档无文字内容", "violations": []}

    client = get_llm_client()
    all_findings: list[str] = []

    for idx, chunk in enumerate(chunks):
        try:
            resp = client.chat.completions.create(
                model=MODEL_CHAT,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"请检查以下文字（第{idx+1}段）：\n\n{chunk}"},
                ],
                temperature=0,
                max_tokens=512,
            )
            result = resp.choices[0].message.content.strip()
            if result and result != "无":
                for line in result.splitlines():
                    line = line.strip()
                    if line and line != "无":
                        all_findings.append(f"（第{idx+1}段）{line}")
        except Exception as e:
            all_findings.append(f"（第{idx+1}段）LLM 扫描失败：{e}")

    passed = len(all_findings) == 0
    detail = "未发现可识别身份的信息" if passed else f"发现 {len(all_findings)} 处疑似身份信息"
    return {"passed": passed, "detail": detail, "violations": all_findings}
