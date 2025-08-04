import argparse
import os
import sys
import warnings

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

from tiktok_uploader import Video, login, upload_video
from tiktok_uploader.utils.basics import eprint
from tiktok_uploader.config.settings import Config
from editor import process_videos
from twitch import download_clips
from scheduler import schedule_upload


def main(argv=None):
    """Entry point for the CLI interface."""
    if argv is None:
        argv = sys.argv[1:]


    _ = Config.load("./config.txt")

    parser = argparse.ArgumentParser(
        description="TikTokAutoUpload CLI: загрузка и планирование видео"
        )
    subparsers = parser.add_subparsers(dest="subcommand")

    # Login subcommand.
    login_parser = subparsers.add_parser("login", help="Войти в TikTok и сохранить cookies")
    login_parser.add_argument("-n", "--name", help="Имя для сохранения cookie", required=True)

    # Upload subcommand.
    upload_parser = subparsers.add_parser("upload", help="Загрузить видео в TikTok")
    upload_parser.add_argument("-u", "--users", help="Имя cookie, полученное при login", required=True)
    upload_parser.add_argument("-v", "--video", help="Путь к видеофайлу")
    upload_parser.add_argument("-yt", "--youtube", help="URL Youtube")
    upload_parser.add_argument("-t", "--title", help="Заголовок видео", required=True)
    upload_parser.add_argument("-sc", "--schedule", type=int, default=0, help="Время планирования в секундах")
    upload_parser.add_argument("-ct", "--comment", type=int, default=1, choices=[0, 1])
    upload_parser.add_argument("-d", "--duet", type=int, default=0, choices=[0, 1])
    upload_parser.add_argument("-st", "--stitch", type=int, default=0, choices=[0, 1])
    upload_parser.add_argument("-vi", "--visibility", type=int, default=0, help="Тип видимости: 0 - публичное, 1 - приватное")
    upload_parser.add_argument("-bo", "--brandorganic", type=int, default=0)
    upload_parser.add_argument("-bc", "--brandcontent", type=int, default=0)
    upload_parser.add_argument("-ai", "--ailabel", type=int, default=0)
    upload_parser.add_argument("-p", "--proxy", default="")

    # Show cookies
    show_parser = subparsers.add_parser("show", help="Показать доступных пользователей и видео")
    show_parser.add_argument("-u", "--users", action="store_true", help="Показать все сохранённые cookies")
    show_parser.add_argument("-v", "--videos", action="store_true", help="Показать все видео")

    edit_parser = subparsers.add_parser("edit", help="Пакетное редактирование видео")
    edit_parser.add_argument("src", help="Каталог с исходными видео")
    edit_parser.add_argument("dst", help="Каталог для сохранения")
    edit_parser.add_argument("--start", type=float, default=None)
    edit_parser.add_argument("--end", type=float, default=None)
    edit_parser.add_argument("--rotate", type=int, default=None)
    edit_parser.add_argument("--speed", type=float, default=None)

    fetch_parser = subparsers.add_parser("fetch", help="Скачать клипы с Twitch")
    fetch_parser.add_argument("urls", nargs="+", help="Ссылки на клипы")
    fetch_parser.add_argument("--out", default="clips", help="Каталог для сохранения")

    sched_parser = subparsers.add_parser("schedule", help="Запланировать загрузку видео")
    sched_parser.add_argument("accounts", help="Файл с аккаунтами")
    sched_parser.add_argument("video", help="Видео для загрузки")
    sched_parser.add_argument("title", help="Заголовок")
    sched_parser.add_argument("time", help="Время в формате YYYY-MM-DDTHH:MM")

    # Parse the command-line arguments
    args = parser.parse_args(argv)

    if args.subcommand == "login":
        if not hasattr(args, 'name') or args.name is None:
            parser.error("Параметр --name обязателен для подкоманды login")
        # Name of file to save the session id.
        login_name = args.name
        # Name of file to save the session id.
        login(login_name)

    elif args.subcommand == "upload":
        # Obtain session id from the cookie name.
        if not hasattr(args, 'users') or args.users is None:
            parser.error("Параметр --users обязателен для подкоманды upload")
        
        # Check if source exists,
        if args.video is None and args.youtube is None:
            eprint("Не указан источник. Используйте -v или -yt")
            sys.exit(1)
        if args.video and args.youtube:
            eprint("Флаги -v и -yt нельзя использовать одновременно")
            sys.exit(1)

        if args.youtube:
            video_obj = Video(args.youtube, args.title)
            video_obj.is_valid_file_format()
            video = video_obj.source_ref
            args.video = video
        else:
            if not os.path.exists(os.path.join(os.getcwd(), Config.get().videos_dir, args.video)) and args.video:
                print("[-] Видео не найдено")
                print("Доступные видео:")
                video_dir = os.path.join(os.getcwd(), Config.get().videos_dir)
                for name in os.listdir(video_dir):
                    print(f'[-] {name}')
                sys.exit(1)

        upload_video(
            args.users,
            args.video,
            args.title,
            args.schedule,
            args.comment,
            args.duet,
            args.stitch,
            args.visibility,
            args.brandorganic,
            args.brandcontent,
            args.ailabel,
            args.proxy,
        )

    elif args.subcommand == "show":
        # if flag is c then show cookie names
        if args.users:
            print("Сохранённые пользователи:")
            cookie_dir = os.path.join(os.getcwd(), Config.get().cookies_dir)
            for name in os.listdir(cookie_dir):
                if name.startswith("tiktok_session-"):
                    print(f'[-] {name.split("tiktok_session-")[1]}')

        # if flag is v then show video names
        if args.videos:
            print("Список видео:")
            video_dir = os.path.join(os.getcwd(), Config.get().videos_dir)
            for name in os.listdir(video_dir):
                print(f'[-] {name}')
        elif not args.users and not args.videos:
            print("Не указан флаг. Используйте -u или -v")
    elif args.subcommand == "edit":
        for _ in process_videos(
            args.src, args.dst, start=args.start, end=args.end, rotate=args.rotate, speed=args.speed
        ):
            pass
        print("Готово")
    elif args.subcommand == "fetch":
        download_clips(args.urls, args.out)
        print("Загрузка завершена")
    elif args.subcommand == "schedule":
        from datetime import datetime

        when = datetime.fromisoformat(args.time)
        job_id = schedule_upload(when, args.accounts, args.video, args.title)
        print(f"Задача запланирована: {job_id}")
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    main()
