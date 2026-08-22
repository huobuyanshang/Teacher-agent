import datetime
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_DIR, OUTPUT_DIR, settings
from .lecturer import Lecturer
from .schemas import GenerateRequest

app = FastAPI(title="Agent 讲师", description="调用 DeepSeek 生成可保存的 HTML 课程文件")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

lecturer = Lecturer()


@app.get("/api/health")
async def health() -> dict:
    return {
        "ok": True,
        "mode": "deepseek" if settings.deepseek_api_key else "no-key",
        "has_api_key": bool(settings.deepseek_api_key),
    }


@app.post("/api/generate")
async def generate(request: GenerateRequest) -> dict:
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="请填写要学习的主题")
    try:
        return await lecturer.create_lecture(
            topic=topic,
            api_key=request.api_key,
            model=request.model,
            max_tokens=request.max_tokens,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/courses")
async def list_courses() -> dict:
    courses = []
    for path in sorted(
        OUTPUT_DIR.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True
    ):
        courses.append(
            {
                "filename": path.name,
                "file_url": f"/outputs/{path.name}",
                "title": _extract_title(path),
                "modified_at": _format_time(path.stat().st_mtime),
            }
        )
    return {"courses": courses}


def _extract_title(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")[:2048]
        match = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
        if match:
            return match.group(1).strip()
    except OSError:
        pass
    return path.stem


def _format_time(timestamp: float) -> str:
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
