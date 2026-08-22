import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import OUTPUT_DIR, settings
from .deepseek_client import DeepSeekClient
from .html_renderer import render_lecture_html


class Lecturer:
    async def create_lecture(
        self,
        topic: str,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        key = (api_key or "").strip() or settings.deepseek_api_key
        if not key:
            raise ValueError("未配置 DeepSeek API Key，请在 .env 或页面接口设置中填写。")

        client = DeepSeekClient(
            base_url=settings.deepseek_base_url,
            model=settings.deepseek_model,
            max_tokens=settings.max_tokens,
        )
        data = await client.generate_lecture_json(
            topic=topic,
            api_key=key,
            model=model,
            max_tokens=max_tokens,
        )

        lecture = _normalize_lecture(data, topic)
        html_content = render_lecture_html(lecture, topic)
        filename = _build_filename(topic)
        output_path = OUTPUT_DIR / filename
        output_path.write_text(html_content, encoding="utf-8")

        return {
            "title": lecture["title"],
            "filename": filename,
            "file_url": f"/outputs/{filename}",
            "mode": "deepseek",
            "model": model or settings.deepseek_model,
            "generated_at": lecture["generated_at"],
        }


def _normalize_lecture(data: dict[str, Any], topic: str) -> dict[str, Any]:
    lecture = dict(data)
    lecture.setdefault("title", f"{topic} 学习课程")
    lecture.setdefault("summary", "")
    lecture.setdefault("learning_objectives", [])
    lecture.setdefault("chapters", [])
    lecture.setdefault("faq", [])
    lecture.setdefault("common_mistakes", [])
    lecture.setdefault("exercises", [])
    lecture.setdefault("key_takeaways", [])
    lecture.setdefault("related_topics", [])
    lecture["topic"] = topic
    lecture["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return lecture


def _build_filename(topic: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", topic).strip("-") or "lecture"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{slug[:40]}.html"
