"""Работа с видео."""

from __future__ import annotations

import os
import time
from typing import Tuple

from moviepy.editor import AudioFileClip, ColorClip, CompositeVideoClip, TextClip, VideoFileClip
from pytube import YouTube

from ..config.settings import Config


class Video:
    """Класс для обработки видео."""

    _YT_DOMAINS = [
        "http://youtu.be/",
        "https://youtu.be/",
        "http://youtube.com/",
        "https://youtube.com/",
        "https://m.youtube.com/",
        "http://www.youtube.com/",
        "https://www.youtube.com/",
    ]

    def __init__(self, source_ref: str, video_text: str) -> None:
        self.config = Config.get()
        self.source_ref = source_ref
        self.video_text = video_text

        self.source_ref = self.downloadIfYoutubeURL()
        while not os.path.isfile(self.source_ref):
            time.sleep(1)

        self.clip = VideoFileClip(self.source_ref)

    def crop(self, start_time: float, end_time: float, saveFile: bool = False) -> VideoFileClip:
        if end_time > self.clip.duration:
            end_time = self.clip.duration
        save_path = os.path.join(os.getcwd(), self.config.videos_dir, "processed") + ".mp4"
        self.clip = self.clip.subclip(t_start=start_time, t_end=end_time)
        if saveFile:
            self.clip.write_videofile(save_path)
        return self.clip

    def createVideo(self) -> Tuple[str, VideoFileClip]:
        self.clip = self.clip.resize(width=1080)
        base_clip = ColorClip(size=(1080, 1920), color=[10, 10, 10], duration=self.clip.duration)
        bottom_meme_pos = 960 + (((1080 / self.clip.size[0]) * (self.clip.size[1])) / 2) - 20
        if self.video_text:
            try:
                meme_overlay = TextClip(
                    txt=self.video_text,
                    bg_color=self.config.imagemagick_text_background_color,
                    color=self.config.imagemagick_text_foreground_color,
                    size=(900, None),
                    kerning=-1,
                    method="caption",
                    font=self.config.imagemagick_font,
                    fontsize=self.config.imagemagick_font_size,
                    align="center",
                )
            except OSError as e:
                print(
                    "Убедитесь, что ImageMagick установлен и путь к бинарному файлу указан верно"
                )
                print("https://imagemagick.org/script/download.php#windows")
                print(e)
                exit()
            meme_overlay = meme_overlay.set_duration(self.clip.duration)
            self.clip = CompositeVideoClip(
                [base_clip, self.clip.set_position(("center", "center")), meme_overlay.set_position(("center", bottom_meme_pos))]
            )

        dir_path = os.path.join(self.config.post_processing_video_path, "post-processed") + ".mp4"
        self.clip.write_videofile(dir_path, fps=24)
        return dir_path, self.clip

    def is_valid_file_format(self) -> None:
        if not self.source_ref.endswith(".mp4") and not self.source_ref.endswith(".webm"):
            exit(f"Файл {self.source_ref} имеет неверное расширение. Требуется .mp4 или .webm")

    def get_youtube_video(self, max_res: bool = True) -> str | bool:
        url = self.source_ref
        streams = YouTube(url).streams.filter(progressive=True)
        valid_streams = sorted(streams, reverse=True, key=lambda x: x.resolution is not None)
        filtered_streams = sorted(valid_streams, reverse=True, key=lambda x: int(x.resolution.split("p")[0]))
        if filtered_streams:
            selected_stream = filtered_streams[0]
            print("Начинаем загрузку видео...")
            selected_stream.download(output_path=os.path.join(os.getcwd(), Config.get().videos_dir), filename="pre-processed.mp4")
            filename = os.path.join(os.getcwd(), Config.get().videos_dir, "pre-processed.mp4")
            return filename

        video = YouTube(url).streams.filter(file_extension="mp4", adaptive=True).first()
        audio = YouTube(url).streams.filter(file_extension="webm", only_audio=True, adaptive=True).first()
        if video and audio:
            random_filename = str(int(time.time()))
            video_path = os.path.join(os.getcwd(), Config.get().videos_dir, "pre-processed.mp4")
            resolution = int(video.resolution[:-1])
            if resolution >= 360:
                downloaded_v_path = video.download(output_path=os.path.join(os.getcwd(), self.config.videos_dir), filename=random_filename)
                print("Видео загружено @" + video.resolution)
                downloaded_a_path = audio.download(output_path=os.path.join(os.getcwd(), self.config.videos_dir), filename="a" + random_filename)
                print("Аудио загружено")
                file_check_iter = 0
                while not os.path.exists(downloaded_a_path) and os.path.exists(downloaded_v_path):
                    time.sleep(2 ** file_check_iter)
                    file_check_iter += 1
                    if file_check_iter > 3:
                        print("Ошибка при сохранении файлов, попробуйте снова")
                        return False
                    print("Ожидание появления файлов...")

                composite_video = VideoFileClip(downloaded_v_path).set_audio(AudioFileClip(downloaded_a_path))
                composite_video.write_videofile(video_path)
                return video_path
            else:
                print("Все видео слишком низкого качества")
                return False
        print("Нет доступных видео с аудио и видео")
        return False

    def downloadIfYoutubeURL(self) -> str:
        if any(ext in self.source_ref for ext in Video._YT_DOMAINS):
            print("Обнаружена ссылка на YouTube...")
            video_dir = self.get_youtube_video()
            return video_dir if video_dir else self.source_ref
        return self.source_ref
