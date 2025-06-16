"""Утилиты для работы с cookie."""

from __future__ import annotations

import os
import pickle
from typing import List

from ..config.settings import Config
from .basics import eprint


def _cookie_path(filename: str, cookies_path: str | None = None) -> str:
    base = cookies_path or os.path.join(os.getcwd(), Config.get().cookies_dir)
    return os.path.join(base, f"{filename}.cookie")


def load_cookies_from_file(filename: str, cookies_path: str | None = None) -> List[dict]:
    """Загружает cookies из файла."""
    path = _cookie_path(filename, cookies_path)
    if not os.path.exists(path):
        print("Пользователь не найден.")
        return []
    with open(path, "rb") as f:
        cookie_data = pickle.load(f)
    cookies = []
    for cookie in cookie_data:
        if "sameSite" in cookie and cookie["sameSite"] == "None":
            cookie["sameSite"] = "Strict"
        cookies.append(cookie)
    return cookies


def save_cookies_to_file(cookies: List[dict] | None, filename: str, cookies_path: str | None = None) -> None:
    """Сохраняет cookies в файл."""
    path = _cookie_path(filename, cookies_path)
    print("Сохранение cookies в файл:", path)
    with open(path, "wb") as f:
        pickle.dump(cookies, f)


def delete_cookies_file(filename: str, cookies_path: str | None = None) -> None:
    path = _cookie_path(filename, cookies_path)
    if os.path.exists(path):
        os.remove(path)
        print("Файл cookie удалён:", path)
    else:
        print("Файла cookie не существует:", path)


def delete_all_cookies_files(cookies_path: str | None = None) -> None:
    dir_path = cookies_path or os.path.join(os.getcwd(), Config.get().cookies_dir)
    for name in os.listdir(dir_path):
        if name.endswith(".cookie"):
            os.remove(os.path.join(dir_path, name))
            print("Удалён файл cookie:", name)
    print("Удалены все файлы cookie.")


def update_dc_location(filename: str, new_dc_location: str) -> None:
    """Placeholder for updating datacenter location."""
    raise NotImplementedError
