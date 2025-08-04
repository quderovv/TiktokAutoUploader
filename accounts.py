"""Simple account pool management."""

from __future__ import annotations

import json
import secrets
from pathlib import Path
from typing import Dict, List


def load_accounts(path: str) -> List[Dict[str, str]]:
    """Load account credentials from JSON file."""
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def save_accounts(path: str, accounts: List[Dict[str, str]]) -> None:
    """Persist account credentials to JSON file."""
    Path(path).write_text(json.dumps(accounts, indent=2, ensure_ascii=False))


def rotate_password(account: Dict[str, str]) -> str:
    """Generate a new password for ``account`` and return it."""
    new_pass = secrets.token_urlsafe(12)
    account["password"] = new_pass
    return new_pass


class AccountManager:
    """Utility helper for batch uploading with password rotation."""

    def __init__(self, store: str):
        self.store = store
        self.accounts = load_accounts(store)

    def upload_all(self, video: str, title: str, **upload_kwargs) -> None:
        """Upload ``video`` for every account concurrently."""
        from concurrent.futures import ThreadPoolExecutor
        from tiktok_uploader import login, upload_video

        def worker(acc: Dict[str, str]):
            user = acc["username"]
            login(user)
            upload_video(user, video, title, **upload_kwargs)
            rotate_password(acc)

        with ThreadPoolExecutor(max_workers=len(self.accounts) or 1) as ex:
            list(ex.map(worker, self.accounts))
        save_accounts(self.store, self.accounts)
