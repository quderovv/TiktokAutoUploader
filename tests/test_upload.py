import pytest
from tiktok_uploader.upload.uploader import upload_video


def test_invalid_schedule_time(monkeypatch):
    def dummy_load(name):
        return [{'name': 'sessionid', 'value': 'abc'}, {'name': 'tt-target-idc', 'value': '1'}]
    monkeypatch.setattr('tiktok_uploader.upload.uploader.load_cookies_from_file', dummy_load)
    monkeypatch.setattr('tiktok_uploader.upload.uploader.upload_to_tiktok', lambda *a, **k: None)
    monkeypatch.setattr('tiktok_uploader.upload.uploader.requests', type('R', (), {'Session': lambda: type("S", (), {'cookies': type("C", (), {'set': lambda *a, **k: None}), 'verify': True, 'headers': {}, 'post': lambda *a, **k: type("Resp", (), {'status_code':200, 'json': lambda :{"project":{"project_id":1}}}), 'head': lambda *a, **k: type("Resp", (), {'status_code':200})})}) )
    assert not upload_video('user', 'video.mp4', 'title', schedule_time=865000)


def test_title_length(monkeypatch):
    monkeypatch.setattr('tiktok_uploader.upload.uploader.load_cookies_from_file', lambda n: [{'name':'sessionid','value':'1'},{'name':'tt-target-idc','value':'1'}])
    result = upload_video('user', 'video.mp4', 't'*2300)
    assert result is False
