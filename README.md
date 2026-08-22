# Agent 讲师

一个“把 DeepSeek 变成讲师”的小应用：输入一个学习主题，后端调用 DeepSeek 生成结构化课程，并输出一个可以单独保存、打印、分享的 HTML 文件。

## 技术栈

- 后端：Python + FastAPI
- 大模型：DeepSeek API（OpenAI 兼容接口）
- 前端：Vue 3（本地运行库，不依赖 CDN）

## 快速开始

```bash
cd D:\all-project\PythonProjects\agent\teacher

# 1. 配置 API Key
copy .env.example .env
# 编辑 .env，把 DEEPSEEK_API_KEY 改成自己的 key

# 2. 安装依赖（已经装过可以跳过）
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. 启动
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

打开 http://127.0.0.1:8000 ，输入主题（例如“MCP 协议”），点击“生成课程”。

也可以双击 `start_server.bat` 一键启动。

## API Key 配置

服务端从 `.env` 读取 `DEEPSEEK_API_KEY`。未配置时生成接口会返回错误，不会返回演示课程。

API Key 也可以在页面右上角“接口设置”里填写，会保存在浏览器 localStorage，只对当前浏览器生效。

## 配置项

参考 `.env.example`：

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 空 |
| `DEEPSEEK_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 模型名 | `deepseek-chat` |
| `DEEPSEEK_MAX_TOKENS` | 单次生成最大 token | `4000` |

## 生成的文件

课程会保存在 `outputs/` 目录，文件名格式为 `时间-主题.html`。生成后前端会自动加载预览，文件也可以直接拷走单独打开。

## API

- `GET /api/health`：检查服务状态和当前模式
- `POST /api/generate`：生成课程，请求体 `{"topic": "MCP 协议"}`
- `GET /api/courses`：列出已生成的课程
- `GET /outputs/<文件名>`：访问生成的 HTML
