"""
Lightweight local config module.
- No external dependencies.
- Optionally loads environment variables from a .env file (project root or backend/).
- Exposes convenience helpers and common settings.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional


def _parse_env_line(line: str) -> Optional[tuple[str, str]]:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if "=" not in line:
        return None
    key, val = line.split("=", 1)
    key = key.strip()
    val = val.strip().strip("\"\'")  # remove optional quotes
    return key, val


def load_env(explicit_path: Optional[str | os.PathLike] = None, override: bool = False) -> None:
    """
    Load environment variables from a .env file if present.
    Search order:
      1) explicit_path if provided
      2) project_root/.env (where project_root is backend/..)
      3) backend/.env
    If override=False, will not overwrite variables already in os.environ.
    """
    candidate_paths: list[Path] = []

    if explicit_path:
        candidate_paths.append(Path(explicit_path))
    # this file is backend/config.py -> project root is parent of backend
    backend_dir = Path(__file__).resolve().parent
    project_root = backend_dir.parent
    candidate_paths.append(project_root / ".env")
    candidate_paths.append(backend_dir / ".env")

    env_path = next((p for p in candidate_paths if p.is_file()), None)
    if not env_path:
        return

    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            parsed = _parse_env_line(raw)
            if not parsed:
                continue
            key, val = parsed
            if not override and key in os.environ:
                continue
            os.environ[key] = val
    except Exception:
        # Fail silently; config should be non-fatal.
        pass


# Load .env once on import (non-fatal if missing)
load_env()


def get(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get an environment-based setting with an optional default."""
    return os.environ.get(key, default)


# Common settings (add more as needed)
GEMINI_API_KEY: str = get("GEMINI_API_KEY", "") or ""
UVICORN_HOST: str = get("UVICORN_HOST", "0.0.0.0") or "0.0.0.0"
# keep as int if possible
try:
    UVICORN_PORT: int = int(get("UVICORN_PORT", "8000") or 8000)
except ValueError:
    UVICORN_PORT = 8000
