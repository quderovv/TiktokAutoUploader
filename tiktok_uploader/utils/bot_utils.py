"""Вспомогательные функции для загрузки."""

from __future__ import annotations

import json
import re
import secrets
import string
import subprocess
import time
import uuid
import zlib
from typing import Any, Dict, List

import requests
from requests_auth_aws_sigv4 import AWSSigV4

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def subprocess_jsvmp(js: str, ua: str, url: str) -> str | None:
    """Запускает node-скрипт для генерации подписи."""
    proc = subprocess.Popen(["node", js, url, ua], stdout=subprocess.PIPE)
    out = proc.stdout.read().decode("utf-8") if proc.stdout else ""
    return out


def generate_random_string(length: int, underline: bool) -> str:
    """Генерирует случайную строку."""
    chars = string.ascii_letters + string.digits + ("_" if underline else "")
    return "".join(secrets.choice(chars) for _ in range(length))


def crc32(content: bytes) -> str:
    """CRC32 хеш."""
    prev = zlib.crc32(content, 0)
    return ("%X" % (prev & 0xFFFFFFFF)).lower().zfill(8)


def print_response(resp: requests.Response) -> None:
    print(f"{resp.status_code}")
    print(f"{resp.content}")


def print_error(url: str, resp: requests.Response) -> None:
    print(f"[-] Ошибка при обращении к {url}")
    print_response(resp)


def assert_success(url: str, resp: requests.Response) -> bool:
    if resp.status_code != 200:
        print_error(url, resp)
    return resp.status_code == 200


def convert_tags(text: str, session: requests.Session) -> tuple[str, List[Dict[str, Any]]]:
    end = 0
    i = -1
    text_extra: List[Dict[str, Any]] = []

    def text_extra_block(start: int, end: int, type_: int, hashtag_name: str, user_id: str, tag_id: str) -> Dict[str, Any]:
        return {
            "end": end,
            "hashtag_name": hashtag_name,
            "start": start,
            "tag_id": tag_id,
            "type": type_,
            "user_id": user_id,
        }

    def convert(match: re.Match[str]) -> str:
        nonlocal i, end, text_extra
        i += 1
        if match.group(1):
            text_extra.append(text_extra_block(end, end + len(match.group(1)) + 1, 1, match.group(1), "", str(i)))
            end += len(match.group(1)) + 1
            return f"<h id=\"{i}\">#{match.group(1)}</h>"
        if match.group(2):
            url = "https://www.tiktok.com/@" + match.group(2)
            headers = {
                "authority": "www.tiktok.com",
                "accept": "*/*",
                "accept-language": "ru-RU,ru;q=0.9",
                "user-agent": user_agent,
            }
            r = session.request("GET", url, headers=headers)
            user_id = r.text.split('webapp.user-detail":{"userInfo":{"user":{"id":"')[1].split('"')[0]
            text_extra.append(text_extra_block(end, end + len(match.group(2)) + 1, 0, "", user_id, str(i)))
            end += len(match.group(2)) + 1
            return f"<m id=\"{i}\">@{match.group(2)}</m>"
        end += len(match.group(3))
        return match.group(3)

    result = re.sub(r'#(\w+)|@([\w.-]+)|([^#@]+)', convert, text)
    return result, text_extra
