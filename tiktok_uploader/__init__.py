import warnings

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

from .core.browser import Browser
from .utils.cookies import load_cookies_from_file, save_cookies_to_file, delete_cookies_file, delete_all_cookies_files
from .config.settings import Config
from .core.video import Video
from .upload.uploader import login, upload_video
from .utils.basics import eprint

__all__ = [
    'Browser',
    'load_cookies_from_file',
    'save_cookies_to_file',
    'delete_cookies_file',
    'delete_all_cookies_files',
    'Config',
    'Video',
    'login',
    'upload_video',
    'eprint'
]
