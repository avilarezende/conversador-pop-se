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


async def run() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="pt-BR",
        )
        page = await context.new_page()
        page.on("pageerror", lambda err: print("PAGEERROR", err))
        page.on("console", lambda msg: print("CONSOLE", msg.type, msg.text) if msg.type == "error" else None)

        # 1) Login
        await page.goto(BASE, wait_until="networkidle")
        await page.wait_for_selector("#login-form")
        await shot(page, "usage-login.jpg", full_page=False)

        # 2) Login with AD
        await page.check("#use-ad")
        await page.fill("#username", "usuario")
        await page.fill("#password", "usuario")
        await page.click("#login-form button[type=submit]")
        await page.wait_for_selector("#view-app:not([hidden])", timeout=10000)
        await page.wait_for_timeout(900)
        # shares may render as article.place-card
        try:
            await page.wait_for_selector("#shares-grid article, #shares-grid .place-card", timeout=5000)
        except Exception as exc:
            print("WARN shares grid:", exc)
            print("shares HTML:", await page.inner_html("#shares-grid"))
        await shot(page, "usage-portal.jpg", full_page=True)
        await shot(page, "portal-home-ad.jpg", full_page=True)

        # 3) Mount clouds if needed
        for provider in ("onedrive", "google_drive"):
            btn = page.locator(f'[data-action="mount"][data-provider="{provider}"]')
            if await btn.count():
                await btn.first.click()
                await page.wait_for_timeout(900)
        await shot(page, "portal-cloud-mounted.jpg", full_page=True)

        # 4) Open files (home share)
        open_btn = page.locator('[data-action="open"][data-share="home"]')
        if await open_btn.count() == 0:
            # fallback: open first share button
            open_btn = page.locator('#shares-grid [data-action="open"]').first
        else:
            open_btn = open_btn.first
        await open_btn.click()
        await page.wait_for_selector("#panel-files:not([hidden])", timeout=8000)
        await page.wait_for_timeout(800)
        await shot(page, "portal-files.jpg", full_page=True)

        # 5) New folder via dialog
        await page.click("#btn-new-folder")
        await page.wait_for_selector("#name-dialog")
        # ensure dialog is open
        await page.wait_for_function("() => document.getElementById('name-dialog').open")
        await page.fill("#name-dialog-input", "ManualDocs")
        await page.click('#name-dialog-form button[value="ok"]')
        await page.wait_for_timeout(900)
        await shot(page, "portal-files-folder.jpg", full_page=True)

        # 6) Sessions panel
        await page.click('.nav-btn[data-panel="sessions"]')
        await page.wait_for_selector("#panel-sessions:not([hidden])")
        await page.wait_for_timeout(500)
        await shot(page, "portal-sessions.jpg", full_page=True)
        await shot(page, "usage-browser.jpg", full_page=True)
        await shot(page, "usage-session.jpg", full_page=True)

        # 7) Admin dashboard
        await page.click("#btn-logout")
        await page.wait_for_selector("#view-login:not([hidden])")
        await page.fill("#username", "guacadmin")
        await page.fill("#password", "guacadmin")
        await page.check("#use-ad")
        await page.click("#login-form button[type=submit]")
        await page.wait_for_selector("#view-app:not([hidden])")
        await page.wait_for_timeout(800)
        await shot(page, "admin-approvals.jpg", full_page=True)
        await shot(page, "portal-admin-home.jpg", full_page=True)

        # 8) Mockup cover (login)
        await page.click("#btn-logout")
        await page.wait_for_selector("#view-login:not([hidden])")
        await shot(page, "segportal-mockup.jpg", full_page=False)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
