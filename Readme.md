YouTube Downloader

This Python-based YouTube downloader allows you to download YouTube videos and playlists as both video and audio files. It uses the yt-dlp library for handling the downloading process and PyQt5 for the graphical user interface (GUI).
Features

    Download Videos: Download videos in various formats and resolutions.
    Download Audio: Extract audio from YouTube videos and download it in formats such as MP3, AAC, and OGG.
    Playlist Support: Download entire YouTube playlists.
    Progress Display: Real-time progress display for downloads.
    Stop Downloads: Ability to stop a download in progress.
    Error Handling: Displays errors in the GUI if they occur during the download.
    Support on Ko-fi: A button to support the developer via Ko-fi.

Requirements

    Python 3.x
    yt-dlp
    PyQt5

Installation

    Clone the repository:

    bash

git clone https://github.com/yourusername/ytdownloader.git

Navigate to the project directory:

bash

cd ytdownloader

Install the required dependencies:

bash

pip install -r requirements.txt

Alternatively, you can install the dependencies manually:

bash

    pip install yt-dlp PyQt5

Usage

    Run the application:

    bash

    python ytdownloader.py

    Paste the YouTube URL into the text field.

    Select your download options:
        Choose whether to download as Video or Audio.
        Select the video quality or audio format (MP3, AAC, OGG).
        Enable or disable the Download Playlist option.

    Choose a download folder:
        Click "Select Folder" to choose where the downloaded files will be saved.

    Start the download:
        Click the Download button to begin downloading.

    Stop the download (optional):
        You can stop the download in progress by clicking Stop Download.

Error Handling

If an error occurs during the download, it will be displayed in the GUI under the status label.
Future Enhancements

    Automatically detect and handle videos that are unavailable or restricted.
    Additional format options.
    Enhanced logging features.

Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.
Support

If you found this project helpful, consider supporting the developer on Ko-fi:
License

This project is licensed under the MIT License.
