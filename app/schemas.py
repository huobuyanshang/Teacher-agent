from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200, description="要学习的主题")
    api_key: str | None = Field(default=None, description="可选，临时覆盖服务端 API Key")
    model: str | None = Field(default=None, description="可选，覆盖 DeepSeek 模型名")
    max_tokens: int = Field(default=4000, ge=500, le=8000)
