import os
import re
import configparser
import yt_dlp

# === Supported Audio Formats ===
SUPPORTED_FORMATS = ['mp3', 'm4a', 'aac', 'flac', 'opus', 'vorbis', 'wav', 'alac']
FORMATS_WITH_METADATA = ['mp3', 'm4a', 'flac', 'alac']

# === Clean Song Title ===
def sanitize_title(title):
    title = re.sub(r'\s*\[(.*?)\]|\s*\((.*?)\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[\\/:*?"<>|]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()

# === Download One Playlist with Progress ===
def download_playlist(save_path, video_url, audio_format, log_fn, preferred_quality='0', redownload_missing=True):
    os.makedirs(save_path, exist_ok=True)
    log_fn(f"\n📂 Downloading to: {save_path}\n🎵 Format: {audio_format} @ {preferred_quality} kbps\n🔗 URL: {video_url}")
    log_fn(f"🛠 Missing files will be {'re-downloaded' if redownload_missing else 'skipped'}.\n")

    if audio_format not in FORMATS_WITH_METADATA:
        log_fn("⚠️  Metadata and thumbnail embedding are not supported for this format. Skipping them.")

    ydl_extract_opts = {
        'quiet': True,
        'extract_flat': True,
        'dump_single_json': True,
        'cookiefile': 'cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_extract_opts) as ydl:
            try:
                info_dict = ydl.extract_info(video_url, download=False)
            except yt_dlp.utils.DownloadError as e:
                error_message = str(e).lower()
                if 'sign in to confirm' in error_message or 'cookies' in error_message:
                    log_fn("❌ Cookie error: This playlist/video requires login. Check your cookies.txt.")
                    input("\nPress Enter to exit...")
                    return
                else:
                    log_fn(f"❌ Failed to extract playlist: {e}")
                    input("\nPress Enter to exit...")
                    return

            entries = info_dict.get('entries', [])
            total_videos = len(entries)
            missing_count = 0
            skipped_count = 0

        for i, entry in enumerate(entries, 1):
            raw_title = entry.get('title', 'Unknown Title')
            title = sanitize_title(raw_title)
            video = entry.get('url')
            video_id = entry.get('id', None)
            log_fn(f"[{i}/{total_videos}] Checking: {title}")

            filename_no_ext = os.path.join(save_path, f"{title}")
            file_check_path = f"{filename_no_ext}.{audio_format}"
            download_archive_path = os.path.join(save_path, 'downloaded.txt')

            if video_id:
                archive_tag = f"youtube {video_id}".strip()
                in_archive = False

                if os.path.exists(download_archive_path):
                    with open(download_archive_path, 'r', encoding='utf-8') as f:
                        archive_lines = f.readlines()
                        in_archive = any(archive_tag in line for line in archive_lines)

                if in_archive and not os.path.exists(file_check_path):
                    if redownload_missing:
                        archive_lines = [line for line in archive_lines if archive_tag not in line]
                        with open(download_archive_path, 'w', encoding='utf-8') as f:
                            f.writelines(archive_lines)
                        log_fn(f"🔁 Will re-download missing file: {title}")
                        missing_count += 1
                    else:
                        log_fn(f"⏩ Skipping missing file (listed as downloaded): {title}")
                        skipped_count += 1
                        continue

            filename = os.path.join(save_path, f"{title}.%(ext)s")

            postprocessors = [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': preferred_quality,
                }
            ]

            if audio_format in FORMATS_WITH_METADATA:
                postprocessors.extend([
                    {'key': 'FFmpegMetadata'},
                    {'key': 'EmbedThumbnail'},
                ])

            ydl_opts = {
                'format': f'bestaudio[ext={audio_format}]/bestaudio/best',
                'outtmpl': filename,
                'cookiefile': 'cookies.txt',
                'ignoreerrors': True,
                'download_archive': download_archive_path,
                'retries': 3,
                'fragment_retries': 3,
                'quiet': True,
                'no_warnings': True,
                'writethumbnail': audio_format in FORMATS_WITH_METADATA,
                'postprocessors': postprocessors,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([video])
                except Exception as e:
                    log_fn(f"❌ Error downloading {title}: {e}")

        log_fn(f"\n🔁 Re-downloaded: {missing_count} | ⏩ Skipped missing: {skipped_count} | ✅ Done.")

    except Exception as e:
        log_fn(f"❌ Unexpected error: {e}")
        input("\nPress Enter to exit...")
        return


# === Console Logging ===
def log_console(msg):
    print(msg)


# === Load from input.txt ===
def load_playlists_from_file(file_path):
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')
    playlists = []
    for section in config.sections():
        if section.lower() == "manual":
            continue
        save_path = config[section].get('save_path')
        video_url = config[section].get('video_url')
        audio_format = config[section].get('audio_format', 'm4a').lower()
        preferred_quality = config[section].get('preferred_quality', '0')
        redownload_missing = config[section].getboolean('redownload_missing', fallback=True)
        if save_path and video_url:
            playlists.append((save_path, video_url, audio_format, preferred_quality, redownload_missing))
    return playlists


# === Main Script ===
def main():
    use_file = input("Batch mode? (y/n): ").strip().lower()

    config_file = 'input.txt'
    if not os.path.exists(config_file):
        print(f"❌ input.txt not found in current directory: {os.getcwd()}")
        input("\nPress Enter to exit...")
        return

    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')

    if use_file == 'y':
        playlists = load_playlists_from_file(config_file)
        if not playlists:
            print("❌ No valid playlist entries found in input.txt")
            input("\nPress Enter to exit...")
            return

        for save_path, video_url, audio_format, preferred_quality, redownload_missing in playlists:
            download_playlist(save_path, video_url, audio_format, log_console, preferred_quality, redownload_missing)

    else:
        user_url = input("Paste YouTube playlist URL: ").strip()
        if not user_url:
            print("❌ No URL provided.")
            input("\nPress Enter to exit...")
            return

        if 'manual' not in config:
            print("❌ [manual] section not found in input.txt")
            input("\nPress Enter to exit...")
            return

        manual_section = config['manual']
        save_path = manual_section.get('save_path')
        audio_format = manual_section.get('audio_format', 'm4a').lower()
        preferred_quality = manual_section.get('preferred_quality', '0')
        redownload_missing = manual_section.getboolean('redownload_missing', fallback=True)

        if not save_path:
            print("❌ Missing 'save_path' in [manual] section.")
            input("\nPress Enter to exit...")
            return

        if audio_format not in SUPPORTED_FORMATS:
            print(f"❌ Unsupported audio format: {audio_format}. Falling back to 'm4a'.")
            audio_format = 'm4a'

        print(f"\nUsing manual settings:")
        print(f"Download Path: {save_path}")
        print(f"Audio Format: {audio_format} @ {preferred_quality} kbps")
        print(f"Redownload Missing Files: {redownload_missing}")

        download_playlist(save_path, user_url, audio_format, log_console, preferred_quality, redownload_missing)

    print("\n✅ All downloads completed.")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
