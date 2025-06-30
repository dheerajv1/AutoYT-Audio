# 🎵 AutoYT-Audio

**AutoYT-Audio** is a Python-based YouTube and YouTube Music **playlist downloader** that extracts high-quality audio in formats like `.mp3`, `.m4a`, `.aac`and more using `yt-dlp` and `FFmpeg`. It supports both manual downloads and batch processing via `input.txt`. This tool supports **playlist URLs only** — single video downloads are not supported.

---

## 🚀 Features

- 🎧 Download audio from YouTube and YouTube Music
- 📁 Output as `.mp3`, `.m4a`, `.aac`, `.wav` etc.
- 📂 Batch download from multiple playlists
- 🔁 Skip or re-download missing files
- 🧠 Smart duplicate detection
- 🎨 Metadata and thumbnail embedding (for supported formats)
- 🔐 Private playlist support via `cookies.txt`
- 🎚️ Customizable bitrate (128 / 192 / 256 / auto)

---

## ⚙️ Requirements

- Python
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)-"Only python repository is required"
- [FFmpeg](https://ffmpeg.org/download.html)

```bash
pip install yt-dlp
```

---

## 📁 Project Structure

```
auto-yt-audio/
├── downloader.py         # Main script
├── input.txt             # Playlist and settings configuration
├── cookies.txt           # Exported cookies for private playlist access
├── run_downloader.bat    # One-click Windows launcher
├── README.md             # This file
├── LICENSE               # MIT License
└── .gitignore            # Ignore compiled files, cookies, etc.
```

---

## 📄 `input.txt` Format

Use `input.txt` to define **multiple playlists** for batch downloading. Each playlist section must have a unique name like `[playlist1]`, `[playlist2]`, etc. The `[manual]` section is used only for manual mode.

```ini
[manual]
save_path = F:\Music\Manual
audio_format = m4a
preferred_quality = 256
redownload_missing = true

[playlist1]
save_path = F:\Music\Lofi
video_url = https://youtube.com/playlist?list=XXXX
audio_format = mp3
preferred_quality = 192
redownload_missing = false

[playlist2]
save_path = F:\Music\Workout
video_url = https://youtube.com/playlist?list=YYYY
audio_format = m4a
preferred_quality = 256
redownload_missing = true
```

| Key                  | Description                                                  |
| --------------------|--------------------------------------------------------------|
| `save_path`         | Folder to save audio files                                   |
| `video_url`         | Playlist URL (YouTube or YouTube Music)                      |
| `audio_format`      | One of `mp3`, `m4a`, `aac`, `wav`, etc.       |
| `preferred_quality` | Audio bitrate: 128 / 192 / 256  / `0` for best available |
| `redownload_missing`| Re-download if file was deleted (`true` or `false`)          |



---

## 🎚️ Bitrate (Quality) Options

| Value | Quality                            |
|-------|------------------------------------|
| 128   | Medium (smallest file size)        |
| 192   | Good balance                       |
| 256   | High quality (recommended)         |
| 0     | Auto / Best from YouTube           |

---

## ▶️ How to Use

Run the script:

```bash
python downloader.py
```

When prompted:

```text
Batch mode? (y/n):
```

- Enter `y` to download from all playlist sections in `input.txt`
- Enter `n` to manually paste a playlist URL (uses `[manual]` settings)

---

## 🖼 Metadata & Thumbnail Support

- Automatically embeds **thumbnails** and **tags** using FFmpeg
- Applies only to formats that support metadata: `mp3`, `m4a`

---

## 🔐 Private / Liked Playlists

1. Use [Get cookies.txt](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Export while logged in to YouTube
3. Save file as `cookies.txt` in the project folder

Script will automatically use this if present.

---

## 🖱️ Windows One-Click Launcher

Use `run_downloader.bat`:

```bat
@echo off
cd /d "%~dp0"
python downloader.py
pause
```

---


## 📃 License

MIT License – Feel free to use or modify.

---

## 🙏 Credits

- Built using [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Audio processed by [FFmpeg](https://ffmpeg.org/)
