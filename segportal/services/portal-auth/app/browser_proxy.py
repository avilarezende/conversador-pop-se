"""Proxy HTTP simples para o navegador embutido do portal."""

from __future__ import annotations

import html
import re
from urllib.parse import quote, urljoin, urlparse

import httpx
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, Response


USER_AGENT = (
    "Mozilla/5.0 (compatible; SegPortalBrowser/1.0; +https://github.com/avilarezende/segportal)"
)


def normalize_url(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        raise HTTPException(status_code=400, detail="URL vazia")
    if value.startswith("//"):
        value = "https:" + value
    if not re.match(r"^https?://", value, flags=re.I):
        value = "https://" + value
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(status_code=400, detail="URL inválida")
    return value


def _proxy_link(target: str) -> str:
    return f"/api/browser/proxy?url={quote(target, safe='')}"


def _rewrite_html(base_url: str, body: str) -> str:
    def repl_attr(match: re.Match[str]) -> str:
        attr = match.group(1)
        quote_char = match.group(2)
        raw = match.group(3)
        if raw.startswith(("data:", "javascript:", "mailto:", "#", "blob:")):
            return match.group(0)
        absolute = urljoin(base_url, raw)
        if absolute.startswith(("http://", "https://")):
            return f'{attr}={quote_char}{_proxy_link(absolute)}{quote_char}'
        return match.group(0)

    rewritten = re.sub(
        r'\b(href|src|action)=([\'"])([^\'"]+)\2',
        repl_attr,
        body,
        flags=re.I,
    )
    banner = (
        '<div id="segportal-browser-banner" style="'
        "position:sticky;top:0;z-index:2147483647;background:#0f2744;color:#fff;"
        "padding:8px 12px;font:13px/1.4 system-ui,sans-serif;"
        'border-bottom:1px solid rgba(255,255,255,.2)">'
        f"Navegando via SegPortal: {html.escape(base_url)}"
        "</div>"
    )
    base_tag = f'<base href="{html.escape(base_url)}">'
    inject = base_tag + banner
    if re.search(r"<body[^>]*>", rewritten, flags=re.I):
        return re.sub(r"(<body[^>]*>)", r"\1" + inject, rewritten, count=1, flags=re.I)
    return inject + rewritten


async def proxy_page(raw_url: str, user=None) -> Response:
    url = normalize_url(raw_url)
    if user is not None:
        from .proxy_policy import assert_url_allowed

        assert_url_allowed(url, user)
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=20.0,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,*/*"},
        ) as client:
            upstream = await client.get(url)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao buscar URL: {exc}") from exc

    content_type = (upstream.headers.get("content-type") or "text/html").split(";")[0].strip().lower()
    if content_type in {"text/html", "application/xhtml+xml", "application/xml", "text/xml"} or not content_type:
        text = upstream.text
        return HTMLResponse(content=_rewrite_html(str(upstream.url), text), status_code=200)

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=content_type or "application/octet-stream",
        headers={"Cache-Control": "no-store"},
    )
