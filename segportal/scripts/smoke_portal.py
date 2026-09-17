#!/usr/bin/env python3
"""Smoke test funcional do portal-auth (stack local).

Uso:
  python3 scripts/smoke_portal.py
  PORTAL_URL=http://127.0.0.1:8090 python3 scripts/smoke_portal.py
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http.cookiejar import CookieJar

BASE = os.environ.get("PORTAL_URL", "http://127.0.0.1:8090").rstrip("/")


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, ok, detail))
        print(f"[{'OK' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    def api(method: str, path: str, payload: dict | None = None):
        data = None
        headers: dict[str, str] = {}
        if payload is not None:
            data = json.dumps(payload).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
        with opener.open(req, timeout=15) as resp:
            raw = resp.read()
            body = json.loads(raw.decode()) if raw else None
            return resp.status, body

    def api_allow(method: str, path: str, payload: dict | None, allowed: set[int]):
        try:
            return api(method, path, payload)
        except urllib.error.HTTPError as exc:
            if exc.code in allowed:
                return exc.code, None
            raise

    try:
        st, body = api("GET", "/api/health")
        check("health", st == 200 and body.get("status") == "ok", str(body))
    except Exception as exc:  # noqa: BLE001
        check("health", False, str(exc))

    try:
        with urllib.request.urlopen(BASE + "/", timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            lower = html.lower()
            check("ui_open_computers", "Abrir Computadores" in html)
            check("ui_nav_browser", "Navegador" in html and 'data-panel="browser"' in html)
            check("ui_nav_computers", "Computadores" in html and 'data-panel="computers"' in html)
            check(
                "ui_hides_guacamole",
                "guacamole" not in lower and "guacadmin" not in lower and "abrir guacamole" not in lower,
            )
    except Exception as exc:  # noqa: BLE001
        check("ui_shell", False, str(exc))

    try:
        st, body = api(
            "POST",
            "/api/login",
            {
                "username": "usuario",
                "password": "usuario",
                "use_active_directory": True,
            },
        )
        check("login_ad", st == 200 and body.get("auth_source") == "ldap", str(body))

        st, dash = api("GET", "/api/dashboard")
        check(
            "dashboard",
            st == 200 and bool(dash.get("shares")) and bool(dash.get("cloud_drives")),
            f"shares={len(dash.get('shares', []))} cloud={len(dash.get('cloud_drives', []))}",
        )
        features = (dash or {}).get("features") or {}
        check("features_embedded_browser", features.get("embedded_browser") is True, str(features))
        check("features_computers", features.get("computers") is True, str(features))
        blob = json.dumps(dash).lower()
        check("dashboard_hides_guacamole", "guacamole" not in blob and "guacadmin" not in blob)

        st, files = api("GET", "/api/files/home")
        check("files_home", st == 200 and "entries" in files, f"n={len(files.get('entries', []))}")

        st, _mk = api_allow(
            "POST",
            "/api/files/home/mkdir",
            {"path": "", "name": "CI_Smoke_Test"},
            {409},
        )
        check("mkdir", st in (200, 409), f"status={st}")

        st, mount = api("POST", "/api/cloud/onedrive/mount", {})
        check("cloud_mount", st == 200 and mount.get("mode") == "demo", str(mount.get("mode")))

        st, cfiles = api("GET", "/api/files/cloud-onedrive")
        check(
            "cloud_files",
            st == 200 and "entries" in cfiles,
            f"n={len(cfiles.get('entries', []))}",
        )

        st, _out = api("POST", "/api/logout", {})
        check("logout", st == 200)

        try:
            api("GET", "/api/dashboard")
            check("auth_required", False, "ainda autenticado")
        except urllib.error.HTTPError as exc:
            check("auth_required", exc.code in (401, 403), f"HTTP {exc.code}")

        st, body = api("POST", "/api/login", {"username": "admin", "password": "admin"})
        check("login_admin", st == 200 and body.get("role") == "admin", str(body.get("role")))
    except Exception as exc:  # noqa: BLE001
        check("portal_flow", False, str(exc))

    failed = [item for item in results if not item[1]]
    print(f"\nTotal: {len(results)} checks, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
