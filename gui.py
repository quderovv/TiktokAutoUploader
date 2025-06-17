import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QFileDialog, QSpinBox, QCheckBox, QComboBox
)
from qt_material import apply_stylesheet

from tiktok_uploader import login, upload_video, Video
from tiktok_uploader.config.settings import Config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        Config.load("./config.txt")
        self.setWindowTitle("TikTok Uploader")
        self.resize(600, 500)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.login_tab = QWidget()
        self.upload_tab = QWidget()
        self.data_tab = QWidget()
        self.tabs.addTab(self.login_tab, "Login")
        self.tabs.addTab(self.upload_tab, "Upload")
        self.tabs.addTab(self.data_tab, "Data")

        self._init_login_tab()
        self._init_upload_tab()
        self._init_data_tab()
        self.refresh_lists()

    def _init_login_tab(self):
        layout = QVBoxLayout()
        self.login_name = QLineEdit()
        self.login_name.setPlaceholderText("Account name")
        self.login_button = QPushButton("Login")
        self.login_output = QLabel()
        layout.addWidget(QLabel("Account name:"))
        layout.addWidget(self.login_name)
        layout.addWidget(self.login_button)
        layout.addWidget(self.login_output)
        self.login_tab.setLayout(layout)
        self.login_button.clicked.connect(self.handle_login)

    def _init_upload_tab(self):
        layout = QVBoxLayout()
        self.user_combo = QComboBox()
        layout.addWidget(QLabel("Account:"))
        layout.addWidget(self.user_combo)

        video_layout = QHBoxLayout()
        self.video_path = QLineEdit()
        self.video_browse = QPushButton("Browse")
        video_layout.addWidget(self.video_path)
        video_layout.addWidget(self.video_browse)
        layout.addWidget(QLabel("Video path:"))
        layout.addLayout(video_layout)
        self.video_browse.clicked.connect(self.browse_video)

        self.youtube_url = QLineEdit()
        layout.addWidget(QLabel("YouTube URL:"))
        layout.addWidget(self.youtube_url)

        self.title_edit = QLineEdit()
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.title_edit)

        self.schedule_spin = QSpinBox()
        self.schedule_spin.setRange(0, 864000)
        layout.addWidget(QLabel("Schedule (sec):"))
        layout.addWidget(self.schedule_spin)

        option_layout = QHBoxLayout()
        self.comment_cb = QCheckBox("Allow comments")
        self.duet_cb = QCheckBox("Allow duet")
        self.stitch_cb = QCheckBox("Allow stitch")
        self.comment_cb.setChecked(True)
        option_layout.addWidget(self.comment_cb)
        option_layout.addWidget(self.duet_cb)
        option_layout.addWidget(self.stitch_cb)
        layout.addLayout(option_layout)

        self.visibility_combo = QComboBox()
        self.visibility_combo.addItems(["Public", "Private"])
        layout.addWidget(QLabel("Visibility:"))
        layout.addWidget(self.visibility_combo)

        self.upload_button = QPushButton("Upload")
        self.upload_output = QLabel()
        layout.addWidget(self.upload_button)
        layout.addWidget(self.upload_output)
        self.upload_tab.setLayout(layout)
        self.upload_button.clicked.connect(self.handle_upload)

    def _init_data_tab(self):
        layout = QVBoxLayout()
        self.users_list = QListWidget()
        self.videos_list = QListWidget()
        self.refresh_button = QPushButton("Refresh")
        layout.addWidget(QLabel("Accounts:"))
        layout.addWidget(self.users_list)
        layout.addWidget(QLabel("Videos:"))
        layout.addWidget(self.videos_list)
        layout.addWidget(self.refresh_button)
        self.data_tab.setLayout(layout)
        self.refresh_button.clicked.connect(self.refresh_lists)

    def cookies_dir(self):
        return os.path.join(os.getcwd(), Config.get().cookies_dir)

    def videos_dir(self):
        return os.path.join(os.getcwd(), Config.get().videos_dir)

    def refresh_accounts(self):
        accounts = []
        dir_path = self.cookies_dir()
        os.makedirs(dir_path, exist_ok=True)
        for name in os.listdir(dir_path):
            if name.startswith("tiktok_session-") and name.endswith(".cookie"):
                accounts.append(name[len("tiktok_session-"):-7])
        self.user_combo.clear()
        self.user_combo.addItems(accounts)
        self.users_list.clear()
        self.users_list.addItems(accounts)

    def refresh_lists(self):
        self.refresh_accounts()
        dir_path = self.videos_dir()
        os.makedirs(dir_path, exist_ok=True)
        self.videos_list.clear()
        for name in os.listdir(dir_path):
            self.videos_list.addItem(name)

    def handle_login(self):
        name = self.login_name.text().strip()
        if not name:
            self.login_output.setText("Enter account name")
            return
        self.login_output.setText("Opening browser...")
        QApplication.processEvents()
        try:
            session_id = login(name)
            self.login_output.setText(f"Logged in as {name}\nSession ID: {session_id}")
            self.refresh_lists()
        except Exception as e:
            self.login_output.setText(str(e))

    def browse_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.webm)")
        if path:
            self.video_path.setText(path)

    def handle_upload(self):
        user = self.user_combo.currentText()
        video = self.video_path.text().strip()
        yt = self.youtube_url.text().strip()
        title = self.title_edit.text().strip()
        schedule = self.schedule_spin.value()
        allow_comment = 1 if self.comment_cb.isChecked() else 0
        allow_duet = 1 if self.duet_cb.isChecked() else 0
        allow_stitch = 1 if self.stitch_cb.isChecked() else 0
        visibility = 0 if self.visibility_combo.currentIndex() == 0 else 1

        if not user:
            self.upload_output.setText("No account selected")
            return
        if not video and not yt:
            self.upload_output.setText("Provide video path or YouTube URL")
            return
        if video and yt:
            self.upload_output.setText("Choose only one source")
            return

        if yt:
            vobj = Video(yt, title)
            vobj.is_valid_file_format()
            video = vobj.source_ref

        if os.path.isabs(video) and os.path.exists(video):
            basename = os.path.basename(video)
            dest = os.path.join(self.videos_dir(), basename)
            if video != dest:
                try:
                    import shutil
                    shutil.copy(video, dest)
                except Exception:
                    pass
            video = basename

        result = upload_video(
            user,
            video,
            title,
            schedule,
            allow_comment,
            allow_duet,
            allow_stitch,
            visibility,
            0,
            0,
            0,
            ""
        )
        if result:
            self.upload_output.setText("Upload successful")
        else:
            self.upload_output.setText("Failed to upload")


def main():
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
