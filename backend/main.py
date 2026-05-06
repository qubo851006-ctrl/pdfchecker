# -*- coding: utf-8 -*-
import io
import fitz
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from checkers import page_checker, font_checker, layout_checker, structure_checker, identity_checker

app = FastAPI(title="暗标格式检查工具")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CHECK_ITEMS = [
    ("page",      "A4纸张与页边距",                page_checker),
    ("font",      "字体字号颜色及格式",              font_checker),
    ("layout",    "行间距、对齐与缩进",              layout_checker),
    ("structure", "封面/目录/页眉/页脚/页码",        structure_checker),
    ("identity",  "可识别身份信息（AI扫描）",         identity_checker),
]


@app.post("/api/check")
async def check_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="请上传 PDF 文件")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50MB 限制
        raise HTTPException(status_code=400, detail="文件过大，请上传 50MB 以内的 PDF")

    try:
        doc = fitz.open(stream=io.BytesIO(content), filetype="pdf")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF 解析失败：{e}")

    results = []
    overall_passed = True

    for key, label, checker in CHECK_ITEMS:
        try:
            result = checker.check(doc)
        except Exception as e:
            result = {"passed": False, "detail": f"检测出错：{e}", "violations": []}

        overall_passed = overall_passed and result["passed"]
        results.append({
            "key":       key,
            "label":     label,
            "passed":    result["passed"],
            "detail":    result["detail"],
            "violations": result.get("violations", []),
        })

    doc.close()
    return {
        "filename":      file.filename,
        "overall_passed": overall_passed,
        "verdict":       "符合要求" if overall_passed else "不符合要求（作否决投标处理）",
        "checks":        results,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
