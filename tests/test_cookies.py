import os
import pickle
from tiktok_uploader.utils.cookies import load_cookies_from_file, save_cookies_to_file
from tiktok_uploader.config.settings import Config


def test_load_cookies_from_file(tmp_path):
    cfg = Config.get()
    cfg._options['COOKIES_DIR'] = str(tmp_path)
    cookie_file = tmp_path / 'test.cookie'
    data = [{'name': 'sessionid', 'value': '123'}]
    with open(cookie_file, 'wb') as f:
        pickle.dump(data, f)
    cookies = load_cookies_from_file('test', cookies_path=str(tmp_path))
    assert cookies[0]['value'] == '123'


def test_save_cookies(tmp_path):
    cfg = Config.get()
    cfg._options['COOKIES_DIR'] = str(tmp_path)
    data = [{'name': 'a', 'value': '1'}]
    save_cookies_to_file(data, 'foo', cookies_path=str(tmp_path))
    path = tmp_path / 'foo.cookie'
    assert path.exists()
