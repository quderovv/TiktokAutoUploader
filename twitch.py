"""Utilities for downloading Twitch clips."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
from typing import Iterable, List


def _download(url: str, output_dir: Path, retries: int) -> bool:
    for _ in range(retries):
        try:
            subprocess.run(
                ["twitch-dl", "download", url, "-o", str(output_dir)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return True
        except subprocess.CalledProcessError:
            continue
    return False


def download_clips(urls: Iterable[str], output_dir: str, retries: int = 3, workers: int = 2) -> List[dict]:
    """Download multiple Twitch clips with retry logic.

    Parameters
    ----------
    urls: Iterable[str]
        Iterable of Twitch clip URLs.
    output_dir: str
        Directory where clips and metadata will be stored.
    retries: int
        Number of download attempts per clip.
    workers: int
        Number of worker threads.
    """

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    queue: Queue[str] = Queue()
    results: List[dict] = []

    for url in urls:
        queue.put(url)

    def worker():
        while True:
            try:
                url = queue.get_nowait()
            except Empty:
                break
            success = _download(url, out, retries)
            meta = {"url": url, "success": success}
            results.append(meta)
            (out / f"{Path(url).name}.json").write_text(
                json.dumps(meta, indent=2, ensure_ascii=False)
            )
            queue.task_done()

    threads = [Thread(target=worker) for _ in range(workers)]
    for t in threads:
        t.start()
    queue.join()
    return results
