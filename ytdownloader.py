import sys
import yt_dlp
import os
import webbrowser
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QRadioButton, QHBoxLayout, QFileDialog, QComboBox, QCheckBox, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


# Worker class to handle the download in a separate thread
class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, video_url, download_format, audio_format, download_folder, video_quality, is_playlist):
        super().__init__()
        self.video_url = video_url
        self.download_format = download_format
        self.audio_format = audio_format
        self.download_folder = download_folder
        self.video_quality = video_quality
        self.is_playlist = is_playlist
        self.is_stopped = False

    def run(self):
        ydl_opts = {
            'ignoreerrors': True,
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.download_progress_hook],
        }

        if self.download_format == "Audio":
            audio_codec = {
                "MP3": "mp3",
                "AAC": "aac",
                "OGG": "vorbis"
            }.get(self.audio_format, "mp3")

            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_codec,
                    'preferredquality': '192',
                }],
                'postprocessor_args': ['-acodec', audio_codec],
            })
        elif self.download_format == "Video":
            ydl_opts.update({'format': self.video_quality})

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

    def stop(self):
        self.is_stopped = True
        self.terminate()  # Force terminate the thread

    def download_progress_hook(self, d):
        if self.is_stopped:
            return
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes')
            if total_bytes:
                percent = int(downloaded_bytes / total_bytes * 100)
                self.progress.emit(percent)


# Main Application Class
class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(100, 100, 500, 350)

        # Layout
        layout = QVBoxLayout()

        # Create top-right layout for Ko-fi button
        top_right_layout = QHBoxLayout()
        top_right_layout.addStretch(1)  # Pushes the button to the far right

        self.kofi_button = QPushButton("Support on Ko-fi")
        self.kofi_button.clicked.connect(self.open_kofi)
        top_right_layout.addWidget(self.kofi_button)

        layout.addLayout(top_right_layout)

        # Label for YouTube URL
        self.url_label = QLabel("YouTube URL:")
        layout.addWidget(self.url_label)

        # Text field for entering the URL
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Enter YouTube video or playlist URL")
        layout.addWidget(self.url_entry)

        # Format selection and playlist checkbox in one row
        format_playlist_layout = QHBoxLayout()

        # Radio buttons for format selection (Video or Audio)
        self.video_radio = QRadioButton("Download Video")
        self.video_radio.setChecked(True)  # Default is Video
        self.audio_radio = QRadioButton("Download Audio")
        format_playlist_layout.addWidget(self.video_radio)
        format_playlist_layout.addWidget(self.audio_radio)

        # Checkbox for downloading playlists
        self.playlist_checkbox = QCheckBox("Download Playlist")
        format_playlist_layout.addWidget(self.playlist_checkbox)

        layout.addLayout(format_playlist_layout)

        # Quality selection for video
        self.quality_label = QLabel("Select Video Quality:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "1080p", "720p", "480p", "360p"])
        self.quality_combo.setEditable(False)
        self.quality_combo.setStyleSheet("QComboBox { text-align: center; }")

        # Audio format selection for audio
        self.audio_format_label = QLabel("Select Audio Format:")
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["MP3", "AAC", "OGG"])
        self.audio_format_combo.setEditable(False)
        self.audio_format_combo.setStyleSheet("QComboBox { text-align: center; }")

        # Place the quality and audio selection into the layout
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_combo)
        layout.addWidget(self.audio_format_label)
        layout.addWidget(self.audio_format_combo)

        # Folder selection in the same row (aligned with video quality)
        folder_layout = QHBoxLayout()

        self.folder_label = QLabel("Download Folder:")
        folder_layout.addWidget(self.folder_label)

        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_button)

        layout.addLayout(folder_layout)

        # Text label to show the selected folder
        self.folder_display = QLabel("Selected Folder: Current Directory")
        layout.addWidget(self.folder_display)

        # Progress bar for downloads
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Button to trigger the download
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        # Button to stop the download
        self.stop_button = QPushButton("Stop Download")
        self.stop_button.clicked.connect(self.stop_download)
        self.stop_button.setEnabled(False)  # Disabled until download starts
        layout.addWidget(self.stop_button)

        # Label for status messages
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Set layout and show window
        self.setLayout(layout)

        # Disable/enable widgets based on the selection (video/audio)
        self.video_radio.toggled.connect(self.toggle_format_options)

        # Set initial state to gray out the unselected options
        self.toggle_format_options()

    def open_kofi(self):
        # Open the Ko-fi page in the default web browser
        webbrowser.open('https://ko-fi.com/drifterduck')

    def toggle_format_options(self):
        if self.video_radio.isChecked():
            self.quality_label.setEnabled(True)
            self.quality_combo.setEnabled(True)
            self.audio_format_label.setEnabled(False)
            self.audio_format_combo.setEnabled(False)
        else:
            self.quality_label.setEnabled(False)
            self.quality_combo.setEnabled(False)
            self.audio_format_label.setEnabled(True)
            self.audio_format_combo.setEnabled(True)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.folder_display.setText(f"Selected Folder: {folder}")
        else:
            self.folder_display.setText("Selected Folder: Current Directory")

    def sanitize_url(self, video_url, is_playlist):
        if not is_playlist:
            video_url = re.sub(r"[&?](list|index)=[^&]+", "", video_url)
        return video_url

    def start_download(self):
        video_url = self.url_entry.text()
        download_format = "Video" if self.video_radio.isChecked() else "Audio"
        video_quality = self.quality_combo.currentText() if download_format == "Video" else None
        audio_format = self.audio_format_combo.currentText() if download_format == "Audio" else None
        download_folder = "." if "Current Directory" in self.folder_display.text() else self.folder_display.text().replace("Selected Folder: ", "")
        is_playlist = self.playlist_checkbox.isChecked()

        video_url = self.sanitize_url(video_url, is_playlist)

        if not video_url.strip():
            self.show_message("Error", "Please enter a valid YouTube URL.")
            return

        self.worker = DownloadWorker(video_url, download_format, audio_format, download_folder, video_quality, is_playlist)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.error_signal.connect(self.show_error_message)
        self.worker.finished_signal.connect(self.download_finished)
        self.worker.start()

        self.stop_button.setEnabled(True)
        self.download_button.setEnabled(False)

    def stop_download(self):
        if self.worker:
            self.worker.stop()
            self.status_label.setText("Download stopped.")
            self.progress_bar.setValue(0)

        self.stop_button.setEnabled(False)
        self.download_button.setEnabled(True)

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def show_error_message(self, message):
        self.status_label.setText(f"Error: {message}")
        self.stop_button.setEnabled(False)
        self.download_button.setEnabled(True)

    def download_finished(self):
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Download completed.")
        self.worker = None  # Clear the worker reference

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)


# Application entry point
app = QApplication(sys.argv)
downloader = YouTubeDownloader()
downloader.show()
sys.exit(app.exec_())
