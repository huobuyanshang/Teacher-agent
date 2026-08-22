from datetime import datetime
from html import escape
from typing import Any

from markdown import markdown


def render_lecture_html(lecture: dict[str, Any], topic: str) -> str:
    title = _text(lecture.get("title")) or f"{topic} 学习课程"
    generated_at = _text(lecture.get("generated_at")) or datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )
    mode_label = "DeepSeek 生成"

    chapters = _chapter_list(lecture.get("chapters"))
    toc_parts = []
    chapter_parts = []
    for index, chapter in enumerate(chapters, start=1):
        chapter_title = _text(chapter.get("title")) or f"第 {index} 章"
        chapter_id = f"chapter-{index}"
        toc_parts.append(
            f'<a href="#{chapter_id}">{index}. {escape(chapter_title)}</a>'
        )
        body_html = _md(_text(chapter.get("content")))
        key_points_html = ""
        key_points = _list(chapter.get("key_points"))
        if key_points:
            key_points_html = (
                '<div class="key-points"><h4>本章要点</h4>'
                + _bullet_list(key_points)
                + "</div>"
            )
        chapter_parts.append(
            f"""
<section class="chapter" id="{chapter_id}">
  <div class="chapter-index">{index}</div>
  <h2>{escape(chapter_title)}</h2>
  <div class="markdown-body">{body_html}</div>
  {key_points_html}
</section>"""
        )

    summary_html = _md(_text(lecture.get("summary")))
    objectives = _list(lecture.get("learning_objectives"))
    objectives_html = (
        '<div class="objectives"><h3>学完这门课，你将能够</h3>'
        + _bullet_list(objectives)
        + "</div>"
        if objectives
        else ""
    )

    mistakes_html = _render_mistakes(lecture.get("common_mistakes"))
    faq_html = _render_faq(lecture.get("faq"))
    exercises_html = _render_exercises(lecture.get("exercises"))
    takeaways_html = _render_takeaways(lecture.get("key_takeaways"))
    related_html = _render_related(lecture.get("related_topics"))
    raw_markdown = _text(lecture.get("raw_markdown"))
    raw_html = (
        f'<section class="chapter" id="full-text"><h2>完整讲义</h2>'
        f'<div class="markdown-body">{_md(raw_markdown)}</div></section>'
        if raw_markdown
        else ""
    )

    html = HTML_TEMPLATE
    html = html.replace("__TITLE__", escape(title))
    html = html.replace("__TOPIC__", escape(topic))
    html = html.replace("__GENERATED_AT__", escape(generated_at))
    html = html.replace("__MODE_LABEL__", escape(mode_label))
    html = html.replace("__TOC__", "\n".join(toc_parts))
    html = html.replace("__SUMMARY__", summary_html)
    html = html.replace("__OBJECTIVES__", objectives_html)
    html = html.replace("__CHAPTERS__", "\n".join(chapter_parts))
    html = html.replace("__MISTAKES__", mistakes_html)
    html = html.replace("__FAQ__", faq_html)
    html = html.replace("__EXERCISES__", exercises_html)
    html = html.replace("__TAKEAWAYS__", takeaways_html)
    html = html.replace("__RELATED__", related_html)
    html = html.replace("__RAW_BODY__", raw_html)
    return html


def _render_mistakes(value: Any) -> str:
    items = _list(value)
    if not items:
        return ""
    parts = ['<section class="block mistakes" id="mistakes"><h2>常见误区与纠正</h2>']
    for index, item in enumerate(items, start=1):
        if isinstance(item, dict):
            mistake = _text(item.get("mistake"))
            correction = _text(item.get("correction"))
        else:
            mistake = str(item)
            correction = ""
        correction_html = (
            f'<div class="fix-row"><span class="badge fix">纠正</span>'
            f'<div class="markdown-body">{_md(correction)}</div></div>'
            if correction
            else ""
        )
        parts.append(
            f'<div class="mistake-item"><span class="badge">误区 {index}</span>'
            f'<div class="markdown-body">{_md(mistake)}</div>{correction_html}</div>'
        )
    parts.append("</section>")
    return "\n".join(parts)


def _render_faq(value: Any) -> str:
    items = _list(value)
    if not items:
        return ""
    parts = ['<section class="block faq" id="faq"><h2>常见问题 FAQ</h2>']
    for item in items:
        if isinstance(item, dict):
            question = _text(item.get("question"))
            answer = _md(_text(item.get("answer")))
        else:
            question = str(item)
            answer = ""
        parts.append(
            f"<details><summary>{escape(question)}</summary>"
            f'<div class="markdown-body">{answer}</div></details>'
        )
    parts.append("</section>")
    return "\n".join(parts)


def _render_exercises(value: Any) -> str:
    items = _list(value)
    if not items:
        return ""
    parts = ['<section class="block exercises" id="exercises"><h2>动手练习</h2>']
    for index, item in enumerate(items, start=1):
        if isinstance(item, dict):
            title = _text(item.get("title"))
            description = _text(item.get("description"))
            expected = _text(item.get("expected_result"))
        else:
            title = f"练习 {index}"
            description = str(item)
            expected = ""
        expected_html = (
            f'<div class="expected"><strong>验收标准：</strong>'
            f'<div class="markdown-body">{_md(expected)}</div></div>'
            if expected
            else ""
        )
        parts.append(
            f'<div class="exercise-item"><div class="exercise-title">{index}. {escape(title)}</div>'
            f'<div class="markdown-body">{_md(description)}</div>{expected_html}</div>'
        )
    parts.append("</section>")
    return "\n".join(parts)


def _render_takeaways(value: Any) -> str:
    items = _list(value)
    if not items:
        return ""
    return (
        '<section class="block takeaways" id="takeaways"><h2>核心结论</h2>'
        + _bullet_list(items)
        + "</section>"
    )


def _render_related(value: Any) -> str:
    items = _list(value)
    if not items:
        return ""
    return (
        '<section class="block related" id="related"><h2>下一步建议</h2>'
        + _bullet_list(items)
        + "</section>"
    )


def _bullet_list(items: list[Any]) -> str:
    return "<ul>" + "".join(f"<li>{_md(str(item))}</li>" for item in items) + "</ul>"


def _chapter_list(value: Any) -> list[dict[str, Any]]:
    raw = _list(value)
    result: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            result.append(item)
        else:
            result.append({"title": "", "content": str(item)})
    return result


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return [value]


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value)


def _md(text: str) -> str:
    return markdown(text or "", extensions=["fenced_code", "tables", "sane_lists"])


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root {
  --ink: #20242a;
  --muted: #667085;
  --paper: #f3f4ee;
  --card: #ffffff;
  --line: #e2e0d8;
  --teal: #0f766e;
  --teal-dark: #0b4f4a;
  --amber: #d97706;
  --code-bg: #0f172a;
  --code-fg: #e2e8f0;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
  line-height: 1.75;
}
.masthead {
  background: linear-gradient(135deg, #0b3d3a 0%, #0f766e 100%);
  color: #fff;
  padding: 54px 24px 40px;
}
.masthead-inner { max-width: 1080px; margin: 0 auto; }
.kicker {
  display: inline-block;
  font-size: 13px;
  text-transform: uppercase;
  border: 1px solid rgba(255,255,255,.45);
  border-radius: 999px;
  padding: 4px 12px;
  margin-bottom: 16px;
}
.masthead h1 {
  margin: 0 0 10px;
  font-size: 38px;
  line-height: 1.25;
  font-weight: 800;
}
.topic-line { margin: 0; color: rgba(255,255,255,.85); font-size: 15px; }
.print-btn {
  margin-top: 20px;
  border: 1px solid rgba(255,255,255,.55);
  background: transparent;
  color: #fff;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}
.print-btn:hover { background: rgba(255,255,255,.12); }
.layout {
  display: flex;
  gap: 34px;
  align-items: flex-start;
  max-width: 1080px;
  margin: 0 auto;
  padding: 30px 24px 70px;
}
.sidebar {
  position: sticky;
  top: 24px;
  flex: 0 0 230px;
  width: 230px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px;
}
.sidebar-title { font-size: 13px; color: var(--muted); margin-bottom: 10px; }
.toc a {
  display: block;
  color: var(--ink);
  text-decoration: none;
  font-size: 14px;
  padding: 7px 8px;
  border-radius: 6px;
  border-left: 3px solid transparent;
}
.toc a:hover { background: #eef6f3; border-left-color: var(--teal); }
.sidebar-meta { margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--line); color: var(--muted); font-size: 12px; }
.content { flex: 1; min-width: 0; }
.block, .chapter {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 24px 26px;
  margin-bottom: 20px;
}
.chapter { border-left: 4px solid var(--teal); position: relative; }
.chapter-index {
  position: absolute;
  top: 18px;
  right: 22px;
  font-size: 40px;
  font-weight: 800;
  color: #dce9e5;
}
.block h2, .chapter h2 { margin: 0 0 14px; font-size: 24px; }
.objectives {
  background: #eef6f3;
  border: 1px solid #cfe4dd;
  border-radius: 8px;
  padding: 14px 18px;
  margin-top: 18px;
}
.objectives h3 { margin: 0 0 8px; font-size: 15px; color: var(--teal-dark); }
.key-points {
  margin-top: 18px;
  background: #fdf8ef;
  border-left: 3px solid var(--amber);
  border-radius: 0 8px 8px 0;
  padding: 12px 16px;
}
.key-points h4 { margin: 0 0 6px; font-size: 14px; color: #92400e; }
.badge {
  display: inline-block;
  background: #fee2e2;
  color: #b91c1c;
  border-radius: 999px;
  font-size: 12px;
  padding: 3px 10px;
  margin-right: 8px;
  vertical-align: middle;
}
.badge.fix { background: #dcfce7; color: #15803d; }
.mistake-item, .exercise-item, .faq details {
  border-top: 1px solid var(--line);
  padding: 14px 0;
}
.mistake-item:first-child, .exercise-item:first-child { border-top: 0; }
.fix-row { display: flex; gap: 10px; margin-top: 10px; }
.fix-row .markdown-body { flex: 1; }
.exercise-title { font-weight: 700; margin-bottom: 6px; }
.expected { background: #f0f9ff; border-radius: 8px; padding: 10px 14px; margin-top: 8px; }
.faq summary { cursor: pointer; font-weight: 600; padding: 6px 0; }
.faq details[open] summary { color: var(--teal-dark); }
.faq .markdown-body { padding: 8px 0 4px; }
.takeaways { background: var(--teal-dark); color: #fff; border: 0; }
.takeaways a { color: #bdeee8; }
.related { background: #fbf7ee; }
.markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4 {
  line-height: 1.35;
  margin: 1.2em 0 .5em;
}
.markdown-body h1 { font-size: 26px; }
.markdown-body h2 { font-size: 22px; }
.markdown-body h3 { font-size: 18px; }
.markdown-body ul, .markdown-body ol { padding-left: 1.4em; }
.markdown-body code {
  background: #e9e8e1;
  color: #8a3d12;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: .92em;
  font-family: Consolas, "Courier New", monospace;
}
.markdown-body pre {
  background: var(--code-bg);
  color: var(--code-fg);
  border-radius: 8px;
  padding: 16px 18px;
  overflow: auto;
  line-height: 1.6;
}
.markdown-body pre code { background: transparent; color: inherit; padding: 0; }
.markdown-body table { border-collapse: collapse; width: 100%; margin: 14px 0; }
.markdown-body th, .markdown-body td {
  border: 1px solid #d5d3cb;
  padding: 8px 10px;
  text-align: left;
}
.markdown-body th { background: #f1f0ea; }
.markdown-body blockquote {
  border-left: 4px solid var(--amber);
  background: #fdf8ef;
  margin: 14px 0;
  padding: 8px 16px;
  border-radius: 0 8px 8px 0;
}
.footer {
  text-align: center;
  color: var(--muted);
  font-size: 13px;
  padding: 26px;
}
@media (max-width: 860px) {
  .layout { flex-direction: column; }
  .sidebar { position: static; width: 100%; }
  .masthead { padding: 36px 20px 30px; }
  .masthead h1 { font-size: 28px; }
  .chapter-index { display: none; }
}
@media print {
  .sidebar, .print-btn, .footer { display: none; }
  body { background: #fff; }
  .block, .chapter { box-shadow: none; border: 1px solid #bbb; break-inside: avoid; }
  .layout { padding: 0; }
}
</style>
</head>
<body>
<header class="masthead">
  <div class="masthead-inner">
    <span class="kicker">Agent 讲师课程</span>
    <h1>__TITLE__</h1>
    <p class="topic-line">学习主题：__TOPIC__ · __GENERATED_AT__ · __MODE_LABEL__</p>
    <button class="print-btn" onclick="window.print()">打印 / 导出 PDF</button>
  </div>
</header>
<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-title">课程目录</div>
    <nav class="toc">__TOC__</nav>
    <div class="sidebar-meta">本文件由 Agent 讲师生成，可单独保存和分享。</div>
  </aside>
  <main class="content">
    <section class="block" id="overview">
      <h2>课程概览</h2>
      <div class="markdown-body">__SUMMARY__</div>
      __OBJECTIVES__
    </section>
    __CHAPTERS__
    __MISTAKES__
    __FAQ__
    __EXERCISES__
    __TAKEAWAYS__
    __RELATED__
    __RAW_BODY__
  </main>
</div>
<footer class="footer">Generated by Agent Lecturer · __GENERATED_AT__</footer>
</body>
</html>
"""
