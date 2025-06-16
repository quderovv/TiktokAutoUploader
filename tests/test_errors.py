from types import SimpleNamespace
from tiktok_uploader.utils.bot_utils import assert_success


def test_assert_success_error(capsys):
    resp = SimpleNamespace(status_code=500, content=b'fail')
    result = assert_success('http://x', resp)
    captured = capsys.readouterr()
    assert 'Ошибка' in captured.out
    assert result is False
