"""Shared bootstrap utilities for local development scripts."""
import asyncio
import os
import selectors
import sys
from pathlib import Path


def setup_path() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _load_env(path: str) -> None:
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def load_envs() -> None:
    _load_env(".envs/local/api.env")
    _load_env(".envs/local/db.env")


def run_async(coro) -> None:
    # Windows defaults to ProactorEventLoop which psycopg async does not support.
    # SelectorEventLoop is required and works on all platforms.
    asyncio.run(
        coro,
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
    )
