#!/usr/bin/env python3
"""Captura screenshots da UI portal-auth para a documentação."""

from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8090"
OUT = Path("/workspace/segportal/docs/images")
OUT.mkdir(parents=True, exist_ok=True)


async def shot(page, name: str, full_page: bool = True) -> None:
    path = OUT / name
    await page.screenshot(path=str(path), full_page=full_page, type="jpeg", quality=88)
    print(f"saved {path} ({path.stat().st_size} bytes)")


async def login(page, username: str, password: str, use_ad: bool = True) -> None:
    await page.goto(BASE, wait_until="networkidle")
    await page.wait_for_selector("#login-form")
    box = page.locator("#use-ad")
    if use_ad:
        await box.check()
    else:
        await box.uncheck()
    await page.fill("#username", username)
    await page.fill("#password", password)
    await page.click("#login-form button[type=submit]")
    await page.wait_for_selector("#view-app:not([hidden])", timeout=15000)
    await page.wait_for_timeout(600)


async def assert_no_guacamole(page) -> None:
    body = (await page.inner_text("body")).lower()
    html = (await page.content()).lower()
    for needle in ("guacamole", "guacadmin", "abrir guacamole", "/guacamole"):
        if needle in body or needle in html:
            raise SystemExit(f"UI ainda expõe: {needle}")


async def goto_panel(page, name: str) -> None:
    await page.click(f'.nav-btn[data-panel="{name}"]')
    await page.wait_for_function(
        """(name) => {
          const el = document.getElementById('panel-' + name);
          return el && !el.hasAttribute('hidden');
        }""",
        arg=name,
    )
    await page.wait_for_timeout(400)


async def run() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="pt-BR",
        )
        page = await context.new_page()
        page.on("pageerror", lambda err: print("PAGEERROR", err))
        page.on(
            "console",
            lambda msg: print("CONSOLE", msg.type, msg.text) if msg.type == "error" else None,
        )

        # 1) Login
        await page.goto(BASE, wait_until="networkidle")
        await page.wait_for_selector("#login-form")
        await assert_no_guacamole(page)
        btn = await page.inner_text("body")
        if "abrir guacamole" in btn.lower():
            raise SystemExit("Login ainda menciona Abrir Guacamole")
        await shot(page, "usage-login.jpg", full_page=False)
        await shot(page, "segportal-mockup.jpg", full_page=False)

        # 2) Usuário com AD
        await login(page, "usuario", "usuario", use_ad=True)
        await assert_no_guacamole(page)
        label = (await page.inner_text("#btn-open-computers")).strip()
        if label != "Abrir Computadores":
            raise SystemExit(f"Botão inesperado no Início: {label!r}")
        try:
            await page.wait_for_selector("#shares-grid article, #shares-grid .place-card", timeout=5000)
        except Exception as exc:
            print("WARN shares:", exc)
            print(await page.inner_html("#shares-grid"))
        await shot(page, "usage-portal.jpg", full_page=True)
        await shot(page, "portal-home-ad.jpg", full_page=True)

        # 3) Montar nuvem
        for provider in ("onedrive", "google_drive"):
            btn = page.locator(f'[data-action="mount"][data-provider="{provider}"]')
            if await btn.count():
                await btn.first.click()
                await page.wait_for_timeout(700)
        await shot(page, "portal-cloud-mounted.jpg", full_page=True)

        # 4) Arquivos
        open_btn = page.locator('[data-action="open"][data-share="home"]')
        if await open_btn.count() == 0:
            open_btn = page.locator('#shares-grid [data-action="open"]').first
        else:
            open_btn = open_btn.first
        await open_btn.click()
        await page.wait_for_function(
            "() => { const el = document.getElementById('panel-files'); return el && !el.hasAttribute('hidden'); }"
        )
        await page.wait_for_timeout(700)
        await shot(page, "portal-files.jpg", full_page=True)
        await shot(page, "usage-files.jpg", full_page=True)

        # 5) Nova pasta
        await page.click("#btn-new-folder")
        await page.wait_for_function("() => document.getElementById('name-dialog').open")
        await page.fill("#name-dialog-input", "ManualDocs")
        await page.click('#name-dialog-form button[value="ok"]')
        await page.wait_for_timeout(800)
        await shot(page, "portal-files-folder.jpg", full_page=True)

        # 6) Aba Navegador embutido
        await goto_panel(page, "browser")
        await assert_no_guacamole(page)
        frame = page.frame_locator("#browser-frame")
        await frame.locator("body").wait_for(timeout=5000)
        await shot(page, "usage-browser.jpg", full_page=True)

        await page.fill("#browser-url", "segportal://bacen")
        await page.click('#browser-url-form button[type="submit"]')
        await page.wait_for_timeout(1200)
        await shot(page, "usage-browser-bacen.jpg", full_page=True)

        # 7) Computadores (botão do Início + aba)
        await goto_panel(page, "home")
        await page.click("#btn-open-computers")
        await page.wait_for_function(
            "() => { const el = document.getElementById('panel-computers'); return el && !el.hasAttribute('hidden'); }"
        )
        await page.wait_for_timeout(600)
        await assert_no_guacamole(page)
        await shot(page, "portal-sessions.jpg", full_page=True)

        connect = page.locator('[data-action="computer"][data-id="desktop-financeiro"]')
        if await connect.count() == 0:
            raise SystemExit("Desktop Financeiro não listado em Computadores")
        await connect.first.click()
        await page.wait_for_function(
            "() => { const el = document.getElementById('computer-session'); return el && !el.hasAttribute('hidden'); }"
        )
        await page.wait_for_timeout(900)
        await shot(page, "usage-session.jpg", full_page=True)

        # 8) Admin
        await page.click("#btn-logout")
        await page.wait_for_selector("#view-login:not([hidden])")
        await login(page, "admin", "admin", use_ad=True)
        await assert_no_guacamole(page)
        await shot(page, "admin-approvals.jpg", full_page=True)
        await shot(page, "portal-admin-home.jpg", full_page=True)

        await browser.close()
        print("capture ok")


if __name__ == "__main__":
    asyncio.run(run())
