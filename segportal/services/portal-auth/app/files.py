"""Operações de arquivos no dashboard pessoal."""

from __future__ import annotations

import mimetypes
import re
import shutil
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile

from .auth import PortalUser
from .config import settings
from .ldap_shares import resolve_share_root

SAFE_NAME = re.compile(r"^[^\\/:*?\"<>|\x00-\x1f]+$")


def _join(root: Path, rel: str) -> Path:
    rel = (rel or "").replace("\\", "/").lstrip("/")
    parts = [p for p in rel.split("/") if p not in ("", ".", "..")]
    target = root.joinpath(*parts).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise HTTPException(status_code=400, detail="Caminho inválido")
    return target


def _meta(path: Path, root: Path) -> dict[str, Any]:
    rel = str(path.relative_to(root)).replace("\\", "/")
    if rel == ".":
        rel = ""
    return {
        "name": path.name,
        "path": rel,
        "is_dir": path.is_dir(),
        "size": path.stat().st_size if path.is_file() else None,
        "modified": int(path.stat().st_mtime),
        "mime": mimetypes.guess_type(path.name)[0] if path.is_file() else None,
    }


def list_dir(user: PortalUser, share_id: str, rel_path: str = "") -> dict[str, Any]:
    try:
        root, share = resolve_share_root(user, share_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    current = _join(root, rel_path)
    if not current.exists() or not current.is_dir():
        raise HTTPException(status_code=404, detail="Pasta não encontrada")

    entries = [
        _meta(child, root)
        for child in sorted(current.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        if not child.name.startswith(".")
    ]
    crumbs = []
    acc: list[str] = []
    for part in (rel_path or "").replace("\\", "/").split("/"):
        if not part:
            continue
        acc.append(part)
        crumbs.append({"name": part, "path": "/".join(acc)})

    return {"share": share, "path": rel_path or "", "breadcrumbs": crumbs, "entries": entries}


async def upload_file(
    user: PortalUser,
    share_id: str,
    rel_path: str,
    upload: UploadFile,
) -> dict[str, Any]:
    root, share = resolve_share_root(user, share_id)
    if share.get("read_only"):
        raise HTTPException(status_code=403, detail="Somente leitura")
    if not upload.filename or not SAFE_NAME.match(upload.filename):
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")

    folder = _join(root, rel_path)
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / upload.filename
    limit = settings.max_upload_mb * 1024 * 1024
    size = 0
    with dest.open("wb") as out:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > limit:
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Arquivo muito grande")
            out.write(chunk)
    return _meta(dest, root)


def mkdir(user: PortalUser, share_id: str, rel_path: str, name: str) -> dict[str, Any]:
    root, share = resolve_share_root(user, share_id)
    if share.get("read_only"):
        raise HTTPException(status_code=403, detail="Somente leitura")
    if not SAFE_NAME.match(name or ""):
        raise HTTPException(status_code=400, detail="Nome inválido")
    parent = _join(root, rel_path)
    parent.mkdir(parents=True, exist_ok=True)
    target = parent / name
    if target.exists():
        raise HTTPException(status_code=409, detail="Já existe")
    target.mkdir()
    return _meta(target, root)


def rename(user: PortalUser, share_id: str, rel_path: str, new_name: str) -> dict[str, Any]:
    root, share = resolve_share_root(user, share_id)
    if share.get("read_only"):
        raise HTTPException(status_code=403, detail="Somente leitura")
    if not SAFE_NAME.match(new_name or ""):
        raise HTTPException(status_code=400, detail="Nome inválido")
    src = _join(root, rel_path)
    if not src.exists():
        raise HTTPException(status_code=404, detail="Não encontrado")
    dest = src.parent / new_name
    if dest.exists():
        raise HTTPException(status_code=409, detail="Já existe")
    src.rename(dest)
    return _meta(dest, root)


def delete(user: PortalUser, share_id: str, rel_path: str) -> dict[str, str]:
    root, share = resolve_share_root(user, share_id)
    if share.get("read_only"):
        raise HTTPException(status_code=403, detail="Somente leitura")
    target = _join(root, rel_path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Não encontrado")
    if target == root:
        raise HTTPException(status_code=400, detail="Não é permitido apagar a raiz")
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    return {"status": "deleted", "path": rel_path}


def open_file_path(user: PortalUser, share_id: str, rel_path: str) -> Path:
    root, _ = resolve_share_root(user, share_id)
    target = _join(root, rel_path)
    if not target.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return target
