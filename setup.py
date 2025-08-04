from setuptools import find_packages, setup

setup(
    name="TikTokAutomation",
    version="1.0.0",
    packages=find_packages(),
    py_modules=[
        "main",
        "cli",
        "editor",
        "watermark",
        "twitch",
        "accounts",
        "scheduler",
    ],
    url="",
    license="",
    author="Michael",
    author_email="ec20433@qmul.ac.uk",
    description="Tiktok Automatic Uploader",
)

