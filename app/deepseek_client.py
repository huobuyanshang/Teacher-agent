import json
import re
from typing import Any

import httpx

from .prompts import LECTURER_SYSTEM_PROMPT


class DeepSeekClient:
    def __init__(self, base_url: str, model: str, max_tokens: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = max_tokens

    async def generate_lecture_json(
        self,
        topic: str,
        api_key: str,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        payload = {
            "model": model or self.model,
            "messages": [
                {"role": "system", "content": LECTURER_SYSTEM_PROMPT},
                {"role": "user", "content": f"请教授我：{topic}"},
            ],
            "temperature": 0.6,
            "max_tokens": max_tokens or self.max_tokens,
            "response_format": {"type": "json_object"},
        }
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 400:
                payload.pop("response_format", None)
                response = await client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                raise RuntimeError(
                    f"DeepSeek API 调用失败（HTTP {response.status_code}）：{response.text[:500]}"
                )
            data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"DeepSeek 返回格式异常：{str(data)[:500]}") from exc
        return _extract_json(content)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    raise RuntimeError("DeepSeek 返回的内容不是合法 JSON，请重试或换一个模型。")
