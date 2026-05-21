!apt update -qq
!apt install -y aria2 ffmpeg p7zip-full
!pip install -q tqdm requests yt-dlp

import os
import re
import json
import time
import socket
import base64
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

import requests
from tqdm.notebook import tqdm
from google.colab import drive
from yt_dlp import YoutubeDL


class AzuDlGC2GD:
    def __init__(self):
        self.project_name = "AzuDl - GC2GD"
        self.project_subtitle = "Azizi Universal Downloader - Google Colab to Google Drive"
        self.version = "1.3.0"

        self.drive_mount_path = Path("/content/drive")
        self.my_drive_path = self.drive_mount_path / "MyDrive"

        self.base_dir = self.my_drive_path / "AzuDl-GC2GD"
        self.torrent_dir = self.base_dir / "TorrentDownloads"
        self.youtube_dir = self.base_dir / "YouTubeDownloads"
        self.direct_dir = self.base_dir / "DirectDownloads"
        self.batch_dir = self.base_dir / "BatchDownloads"
        self.archive_dir = self.base_dir / "Archives"
        self.logs_dir = self.base_dir / "Logs"
        self.history_file = self.logs_dir / "download_history.json"
        self.aria2_session_file = self.logs_dir / "aria2.session"

        self.rpc_url = "http://localhost:6800/jsonrpc"

    def setup(self):
        self.print_banner()
        self.mount_google_drive()
        self.prepare_directories()
        self.start_aria2_rpc()

    def print_banner(self):
        print("=" * 70)
        print(self.project_name)
        print(self.project_subtitle)
        print("Version:", self.version)
        print("=" * 70)

    def mount_google_drive(self):
        if self.my_drive_path.exists():
            print("Google Drive already mounted")
            return

        attempts = [
            {"force_remount": False, "label": "standard mount"},
            {"force_remount": True, "label": "force remount"}
        ]

        last_error = None

        for attempt in attempts:
            try:
                print("Trying Google Drive", attempt["label"])
                drive.mount(str(self.drive_mount_path), force_remount=attempt["force_remount"])

                if self.my_drive_path.exists():
                    print("Google Drive mounted successfully")
                    return

            except Exception as error:
                last_error = error
                print("Mount attempt failed:", error)
                time.sleep(2)

        self.print_drive_mount_help()
        raise RuntimeError(f"Google Drive mount failed: {last_error}")

    def print_drive_mount_help(self):
        print("")
        print("=" * 70)
        print("Google Drive mount failed")
        print("=" * 70)
        print("Try these fixes:")
        print("1. Runtime > Restart session")
        print("2. Run this in a separate cell: from google.colab import drive; drive.flush_and_unmount()")
        print("3. Use only one Google account in your browser")
        print("4. Open Colab in Incognito mode")
        print("5. Make sure third-party cookies are not blocked")
        print("6. Reconnect Google Drive manually from the Colab file panel")
        print("=" * 70)
        print("")

    def prepare_directories(self):
        dirs = [
            self.base_dir,
            self.torrent_dir,
            self.youtube_dir,
            self.direct_dir,
            self.batch_dir,
            self.archive_dir,
            self.logs_dir
        ]

        for item in dirs:
            item.mkdir(parents=True, exist_ok=True)

        if not self.aria2_session_file.exists():
            self.aria2_session_file.write_text("")

    def is_port_open(self, host="127.0.0.1", port=6800):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex((host, port)) == 0

    def start_aria2_rpc(self):
        if self.is_port_open():
            try:
                options = self.rpc("aria2.getGlobalOption")
                save_session = str(options.get("save-session", ""))
                input_file = str(options.get("input-file", ""))

                if str(self.aria2_session_file) in [save_session, input_file]:
                    print("aria2 RPC already running")
                    return

                print("aria2 RPC is running with old options")
                print("Restarting aria2 RPC")
                try:
                    self.rpc("aria2.shutdown")
                    time.sleep(2)
                except Exception:
                    pass

            except Exception:
                pass

        if self.is_port_open():
            subprocess.run(["pkill", "-9", "aria2c"], check=False)
            time.sleep(2)

        cmd = [
            "aria2c",
            "--enable-rpc=true",
            "--rpc-listen-all=false",
            "--rpc-listen-port=6800",
            "--rpc-allow-origin-all=true",
            "--daemon=true",
            "--seed-time=0",
            "--seed-ratio=0.0",
            "--file-allocation=none",
            "--continue=true",
            "--always-resume=true",
            "--auto-save-interval=10",
            "--save-session-interval=10",
            f"--input-file={self.aria2_session_file}",
            f"--save-session={self.aria2_session_file}",
            "--force-save=true",
            "--max-tries=0",
            "--retry-wait=10",
            "--timeout=60",
            "--connect-timeout=60",
            "--enable-dht=true",
            "--enable-dht6=true",
            "--enable-peer-exchange=true",
            "--bt-enable-lpd=true",
            "--bt-save-metadata=true",
            "--bt-load-saved-metadata=true",
            "--console-log-level=warn"
        ]

        subprocess.run(cmd, check=True)

        for _ in range(30):
            if self.is_port_open():
                print("aria2 RPC started")
                print("aria2 session:", self.aria2_session_file)
                return
            time.sleep(0.5)

        raise RuntimeError("Failed to start aria2 RPC server.")

    def rpc(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "id": "azudl-gc2gd",
            "method": method,
            "params": params or []
        }

        response = requests.post(self.rpc_url, json=payload, timeout=30)

        if response.status_code != 200:
            message = response.text[:1000]
            raise RuntimeError(f"aria2 RPC HTTP {response.status_code}: {message}")

        try:
            data = response.json()
        except Exception:
            raise RuntimeError(f"Invalid aria2 RPC response: {response.text[:1000]}")

        if "error" in data:
            raise RuntimeError(data["error"])

        return data["result"]

    def save_aria2_session(self):
        try:
            result = self.rpc("aria2.saveSession")
            print("aria2 session saved")
            return result
        except Exception as error:
            message = str(error)

            if "Filename is not given" in message:
                return None

            print("Failed to save aria2 session:", error)
            return None

    def sanitize_name(self, name):
        name = str(name or "").strip()
        name = re.sub(r'[\/\\:*?"<>|]', "_", name)
        name = re.sub(r"\s+", " ", name)
        return name or f"Download_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

    def format_bytes(self, value):
        value = float(value or 0)

        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if value < 1024:
                return f"{value:.2f} {unit}"
            value /= 1024

        return f"{value:.2f} PB"

    def format_seconds(self, seconds):
        seconds = int(seconds or 0)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"

        return f"{minutes:02d}:{secs:02d}"

    def detect_link_type(self, value):
        value = str(value or "").strip()
        lower = value.lower()

        if lower.startswith("magnet:?"):
            return "torrent"

        parsed = urlparse(value)
        host = parsed.netloc.lower()
        path = parsed.path.lower()

        youtube_hosts = [
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtu.be",
            "music.youtube.com"
        ]

        if any(host == item or host.endswith("." + item) for item in youtube_hosts):
            return "youtube"

        if path.endswith(".torrent"):
            return "torrent_file"

        if lower.startswith(("http://", "https://", "ftp://")):
            return "direct"

        if Path(value).suffix.lower() == ".torrent":
            return "torrent_file"

        return "unknown"

    def save_history(self, item):
        history = []

        if self.history_file.exists():
            try:
                history = json.loads(self.history_file.read_text())
            except Exception:
                history = []

        item["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history.append(item)

        self.history_file.write_text(json.dumps(history, indent=2, ensure_ascii=False))

    def print_history(self):
        if not self.history_file.exists():
            print("No history found")
            return

        try:
            history = json.loads(self.history_file.read_text())
        except Exception:
            print("History file is invalid")
            return

        if not history:
            print("No history found")
            return

        for index, item in enumerate(history[-50:], 1):
            print("-" * 80)
            print("Index:", index)
            print("Type:", item.get("type", "unknown"))
            print("Time:", item.get("time", "unknown"))
            print("Source:", item.get("source", "unknown"))
            print("Output:", item.get("output", "unknown"))
            print("Status:", item.get("status", "unknown"))

            if item.get("format"):
                print("Format:", item.get("format"))

            if item.get("seed") is not None:
                print("Seed:", item.get("seed"))

            if item.get("error"):
                print("Error:", item.get("error"))

    def get_all_downloaded_files(self):
        folders = [
            self.torrent_dir,
            self.youtube_dir,
            self.direct_dir,
            self.batch_dir,
            self.archive_dir
        ]

        files = []

        for folder in folders:
            if folder.exists():
                files.extend([item for item in folder.glob("**/*") if item.is_file()])

        return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

    def get_latest_file(self):
        files = self.get_all_downloaded_files()

        if not files:
            return None

        return files[0]

    def get_latest_downloaded_file(self):
        return self.get_latest_file()

    def get_latest_downloaded_folder(self):
        folders = [
            self.torrent_dir,
            self.youtube_dir,
            self.direct_dir,
            self.batch_dir,
            self.archive_dir
        ]

        all_dirs = []

        for folder in folders:
            if folder.exists():
                all_dirs.extend([item for item in folder.glob("**/*") if item.is_dir()])

        if not all_dirs:
            return None

        return max(all_dirs, key=lambda item: item.stat().st_mtime)

    def list_downloads(self):
        folders = [
            self.torrent_dir,
            self.youtube_dir,
            self.direct_dir,
            self.batch_dir,
            self.archive_dir
        ]

        for folder in folders:
            print("")
            print(str(folder))
            print("-" * 80)

            if not folder.exists():
                print("Folder does not exist")
                continue

            items = sorted(
                folder.glob("**/*"),
                key=lambda x: x.stat().st_mtime if x.exists() else 0,
                reverse=True
            )

            files = [item for item in items if item.is_file()]

            if not files:
                print("No files")
                continue

            for item in files[:100]:
                size = self.format_bytes(item.stat().st_size)
                print(f"{size:<12} {item}")

    def print_latest_file(self):
        latest = self.get_latest_downloaded_file()

        if not latest:
            print("No files found")
            return

        print("Latest file")
        print("-" * 80)
        print("Path:", latest)
        print("Size:", self.format_bytes(latest.stat().st_size))
        print("Modified:", datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

    def select_file(self):
        files = self.get_all_downloaded_files()

        if not files:
            print("No files found")
            return None

        for index, item in enumerate(files[:100], 1):
            print(f"{index:<4} {self.format_bytes(item.stat().st_size):<12} {item}")

        value = input("File number: ").strip()

        if not value.isdigit():
            print("Invalid number")
            return None

        index = int(value)

        if index < 1 or index > min(len(files), 100):
            print("Invalid number")
            return None

        return files[index - 1]

    def add_aria2_download(self, uris, save_dir, speed_limit="", extra_options=None):
        options = {
            "dir": str(save_dir),
            "file-allocation": "none",
            "continue": "true",
            "always-resume": "true",
            "max-tries": "0",
            "retry-wait": "10",
            "timeout": "60",
            "connect-timeout": "60",
            "allow-overwrite": "false",
            "auto-file-renaming": "true",
            "max-connection-per-server": "16",
            "split": "16",
            "min-split-size": "1M"
        }

        if speed_limit:
            options["max-overall-download-limit"] = speed_limit.strip()

        if extra_options:
            options.update(extra_options)

        gid = self.rpc("aria2.addUri", [uris, options])
        self.save_aria2_session()
        return gid

    def add_aria2_torrent(self, torrent_bytes, save_dir, speed_limit="", extra_options=None):
        torrent_base64 = base64.b64encode(torrent_bytes).decode("utf-8")

        options = {
            "dir": str(save_dir),
            "file-allocation": "none",
            "continue": "true",
            "always-resume": "true",
            "max-tries": "0",
            "retry-wait": "10",
            "timeout": "60",
            "connect-timeout": "60",
            "allow-overwrite": "false",
            "auto-file-renaming": "true",
            "seed-time": "0",
            "seed-ratio": "0.0",
            "enable-dht": "true",
            "enable-dht6": "true",
            "enable-peer-exchange": "true",
            "bt-enable-lpd": "true"
        }

        if speed_limit:
            options["max-overall-download-limit"] = speed_limit.strip()

        if extra_options:
            options.update(extra_options)

        gid = self.rpc("aria2.addTorrent", [torrent_base64, [], options])
        self.save_aria2_session()
        return gid

    def fetch_torrent_file_bytes(self, source):
        source = source.strip()

        headers = {
            "User-Agent": "Mozilla/5.0 AzuDl-GC2GD/1.3.0",
            "Accept": "application/x-bittorrent,application/octet-stream,*/*"
        }

        if source.startswith(("http://", "https://")):
            print("Downloading torrent file metadata")
            response = requests.get(source, headers=headers, timeout=60, allow_redirects=True)
            response.raise_for_status()
            content = response.content
        else:
            path = Path(source)

            if not path.exists():
                raise FileNotFoundError(f"Torrent file not found: {path}")

            content = path.read_bytes()

        if not content:
            raise ValueError("Torrent file is empty")

        stripped = content.lstrip()

        if not stripped.startswith(b"d"):
            preview = content[:300].decode("utf-8", errors="replace")
            raise ValueError(
                "Downloaded file is not a valid .torrent file. "
                "The server may have returned HTML, an error page, or blocked the request.\n"
                f"Preview:\n{preview}"
            )

        return content

    def skip_bencode_value(self, data, index):
        token = data[index:index + 1]

        if token == b"i":
            end = data.index(b"e", index)
            return end + 1

        if token in [b"l", b"d"]:
            index += 1

            while data[index:index + 1] != b"e":
                index = self.skip_bencode_value(data, index)

            return index + 1

        if token.isdigit():
            colon = data.index(b":", index)
            length = int(data[index:colon])
            return colon + 1 + length

        raise ValueError("Invalid bencode data")

    def get_torrent_infohash(self, torrent_bytes):
        data = torrent_bytes

        if not data.startswith(b"d"):
            return ""

        index = 1

        while index < len(data) and data[index:index + 1] != b"e":
            key_start = index
            key_end = self.skip_bencode_value(data, key_start)
            key_data = data[key_start:key_end]

            colon = key_data.index(b":")
            key = key_data[colon + 1:]

            value_start = key_end
            value_end = self.skip_bencode_value(data, value_start)

            if key == b"info":
                return hashlib.sha1(data[value_start:value_end]).hexdigest()

            index = value_end

        return ""

    def find_existing_torrent_by_infohash(self, infohash):
        if not infohash:
            return None

        target = str(infohash).lower()
        active, waiting, stopped = self.get_aria2_items()

        for item in active + waiting + stopped:
            bittorrent = item.get("bittorrent", {})
            current = str(bittorrent.get("infoHash", "")).lower()

            if current == target:
                return item

        return None

    def remove_existing_torrent_gid(self, gid):
        if not gid:
            return False

        try:
            self.rpc("aria2.remove", [gid])
            self.save_aria2_session()
            return True
        except Exception:
            pass

        try:
            self.rpc("aria2.removeDownloadResult", [gid])
            self.save_aria2_session()
            return True
        except Exception:
            return False

    def build_torrent_options(self, private=False, seed=False):
        if seed:
            seed_time = "525600"
        else:
            seed_time = "0"

        if private:
            return {
                "seed-time": seed_time,
                "seed-ratio": "0.0",
                "enable-dht": "false",
                "enable-dht6": "false",
                "enable-peer-exchange": "false",
                "bt-enable-lpd": "false",
                "bt-save-metadata": "true",
                "bt-load-saved-metadata": "true",
                "bt-request-peer-speed-limit": "50K"
            }

        return {
            "seed-time": seed_time,
            "seed-ratio": "0.0",
            "enable-dht": "true",
            "enable-dht6": "true",
            "enable-peer-exchange": "true",
            "bt-enable-lpd": "true",
            "bt-save-metadata": "true",
            "bt-load-saved-metadata": "true",
            "bt-request-peer-speed-limit": "50K"
        }

    def get_aria2_status(self, gid):
        keys = [
            "gid",
            "status",
            "totalLength",
            "completedLength",
            "downloadSpeed",
            "uploadSpeed",
            "uploadLength",
            "connections",
            "numSeeders",
            "shareRatio",
            "errorCode",
            "errorMessage",
            "files",
            "bittorrent",
            "followedBy",
            "following",
            "belongsTo"
        ]

        return self.rpc("aria2.tellStatus", [gid, keys])

    def get_aria2_items(self):
        keys = [
            "gid",
            "status",
            "totalLength",
            "completedLength",
            "downloadSpeed",
            "uploadSpeed",
            "uploadLength",
            "connections",
            "numSeeders",
            "shareRatio",
            "errorCode",
            "errorMessage",
            "files",
            "bittorrent",
            "followedBy",
            "following",
            "belongsTo"
        ]

        active = self.rpc("aria2.tellActive", [keys])
        waiting = self.rpc("aria2.tellWaiting", [0, 100, keys])
        stopped = self.rpc("aria2.tellStopped", [0, 100, keys])

        return active, waiting, stopped

    def get_active_waiting_stopped(self):
        return self.get_aria2_items()

    def print_aria2_status(self):
        active, waiting, stopped = self.get_aria2_items()

        groups = [
            ("Active", active),
            ("Waiting", waiting),
            ("Stopped", stopped)
        ]

        for title, items in groups:
            print("")
            print(title)
            print("-" * 80)

            if not items:
                print("No items")
                continue

            for item in items:
                gid = item.get("gid", "")
                status = item.get("status", "")
                total = int(item.get("totalLength", "0") or 0)
                completed = int(item.get("completedLength", "0") or 0)
                speed = int(item.get("downloadSpeed", "0") or 0)
                upload_speed = int(item.get("uploadSpeed", "0") or 0)
                uploaded = int(item.get("uploadLength", "0") or 0)
                share_ratio = item.get("shareRatio", "0")
                connections = item.get("connections", "0")
                seeders = item.get("numSeeders", "0")
                bittorrent = item.get("bittorrent", {})
                infohash = bittorrent.get("infoHash", "")

                percent = 0

                if total > 0:
                    percent = completed * 100 / total

                files = item.get("files", [])
                name = ""

                if files:
                    name = Path(files[0].get("path", "")).name

                print("GID:", gid)
                print("Status:", status)
                print("Name:", name or "unknown")
                print("InfoHash:", infohash or "unknown")
                print("Progress:", f"{percent:.2f}%")
                print("Completed:", self.format_bytes(completed), "/", self.format_bytes(total))
                print("Download Speed:", self.format_bytes(speed) + "/s")
                print("Upload Speed:", self.format_bytes(upload_speed) + "/s")
                print("Uploaded:", self.format_bytes(uploaded))
                print("Ratio:", share_ratio)
                print("Connections:", connections)
                print("Seeders:", seeders)

                if item.get("errorMessage"):
                    print("Error:", item.get("errorMessage"))

                print("-" * 80)

    def purge_aria2_stopped(self):
        try:
            result = self.rpc("aria2.purgeDownloadResult")
            self.save_aria2_session()
            print("Stopped download results cleared")
            print(result)
        except Exception as error:
            print("Failed to purge stopped downloads:", error)

    def remove_aria2_gid(self):
        gid = input("GID to remove: ").strip()

        if not gid:
            print("No GID entered")
            return

        removed = self.remove_existing_torrent_gid(gid)

        if removed:
            print("GID removed:", gid)
        else:
            print("Failed to remove GID:", gid)

    def find_real_torrent_gid(self, metadata_gid, save_dir):
        save_dir = str(save_dir)

        for _ in range(120):
            try:
                status = self.get_aria2_status(metadata_gid)
            except Exception:
                status = {}

            followed_by = status.get("followedBy", [])

            if followed_by:
                real_gid = followed_by[0]
                print("Metadata completed")
                print("Real torrent GID:", real_gid)
                return real_gid

            active, waiting, stopped = self.get_active_waiting_stopped()
            candidates = active + waiting + stopped

            for item in candidates:
                gid = item.get("gid")

                if gid == metadata_gid:
                    continue

                belongs_to = item.get("belongsTo")
                following = item.get("following")

                if belongs_to == metadata_gid or following == metadata_gid:
                    print("Real torrent GID:", gid)
                    return gid

                files = item.get("files", [])

                for file_item in files:
                    path = file_item.get("path", "")

                    if path and str(path).startswith(save_dir):
                        total = int(item.get("totalLength", "0") or 0)

                        if total > 0:
                            print("Real torrent GID:", gid)
                            return gid

            state = status.get("status")

            if state == "error":
                raise RuntimeError(status.get("errorMessage") or "Metadata failed.")

            time.sleep(1)

        print("Could not detect a separate real torrent GID")
        print("Using original GID")
        return metadata_gid

    def wait_for_torrent_metadata(self, gid):
        bar = tqdm(total=1, desc="Fetching metadata", unit="step")

        while True:
            status = self.get_aria2_status(gid)

            if status.get("status") == "error":
                bar.close()
                self.save_aria2_session()
                raise RuntimeError(status.get("errorMessage") or "Metadata fetch failed.")

            followed_by = status.get("followedBy", [])
            files = status.get("files", [])
            total = int(status.get("totalLength", "0") or 0)

            if followed_by:
                bar.update(1)
                bar.close()
                self.save_aria2_session()
                return

            if files and total > 0:
                bittorrent = status.get("bittorrent", {})
                info = bittorrent.get("info", {})

                if info:
                    bar.update(1)
                    bar.close()
                    self.save_aria2_session()
                    return

            if status.get("status") == "complete" and files and total > 0:
                bar.update(1)
                bar.close()
                self.save_aria2_session()
                return

            time.sleep(1)

    def monitor_aria2(self, gid, label, seed=False):
        last_completed = 0
        progress = None
        last_state = None
        printed_file = None
        seeding_notice_printed = False
        seed_started_at = None
        seed_bar = None
        last_session_save = time.time()

        while True:
            status = self.get_aria2_status(gid)

            state = status.get("status")
            total = int(status.get("totalLength", "0") or 0)
            completed = int(status.get("completedLength", "0") or 0)
            speed = int(status.get("downloadSpeed", "0") or 0)
            upload_speed = int(status.get("uploadSpeed", "0") or 0)
            uploaded = int(status.get("uploadLength", "0") or 0)
            seeders = status.get("numSeeders", "0")
            connections = status.get("connections", "0")
            share_ratio = status.get("shareRatio", "0")
            files = status.get("files", [])

            if time.time() - last_session_save >= 30:
                self.save_aria2_session()
                last_session_save = time.time()

            if state != last_state:
                print("Status:", state)
                last_state = state

            if files:
                first_file = files[0].get("path", "")
                if first_file and first_file != printed_file:
                    print("File:", Path(first_file).name)
                    printed_file = first_file

            if state == "error":
                if progress is not None:
                    progress.close()
                if seed_bar is not None:
                    seed_bar.close()
                self.save_aria2_session()
                raise RuntimeError(status.get("errorMessage") or "Download failed.")

            if progress is None and total > 0 and not (seed and completed >= total):
                progress = tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=label
                )

            if progress is not None:
                if completed < last_completed:
                    last_completed = 0
                    progress.n = 0

                delta = completed - last_completed

                if delta > 0:
                    progress.update(delta)

                percent = 0

                if total > 0:
                    percent = completed * 100 / total

                postfix = {
                    "percent": f"{percent:.2f}%",
                    "down": self.format_bytes(speed) + "/s",
                    "up": self.format_bytes(upload_speed) + "/s",
                    "uploaded": self.format_bytes(uploaded),
                    "ratio": str(share_ratio),
                    "connections": connections
                }

                if str(seeders) != "0":
                    postfix["seeders"] = seeders

                progress.set_postfix(postfix)

            last_completed = completed

            if seed and total > 0 and completed >= total:
                if seed_started_at is None:
                    seed_started_at = time.time()

                if not seeding_notice_printed:
                    print("Download completed")
                    print("Seeding is enabled")
                    print("Keep this Colab runtime alive to continue seeding")
                    print("Press interrupt if you want to stop seeding")
                    seeding_notice_printed = True

                    if progress is not None:
                        progress.n = total
                        progress.refresh()
                        progress.close()
                        progress = None

                    seed_bar = tqdm(
                        total=1,
                        unit="step",
                        desc="Seeding Upload"
                    )

                    self.save_aria2_session()

                if seed_bar is not None:
                    elapsed = self.format_seconds(time.time() - seed_started_at)

                    seed_bar.n = 0
                    seed_bar.set_postfix({
                        "up": self.format_bytes(upload_speed) + "/s",
                        "uploaded": self.format_bytes(uploaded),
                        "ratio": str(share_ratio),
                        "connections": connections,
                        "seeders": seeders,
                        "time": elapsed
                    })
                    seed_bar.refresh()

            if state == "complete" and not seed:
                if progress is not None:
                    progress.n = total
                    progress.refresh()
                    progress.close()
                self.save_aria2_session()
                return status

            if state == "complete" and seed:
                time.sleep(5)
                continue

            time.sleep(1)

    def download_magnet(self, magnet, folder_name="", speed_limit="", private=False, seed=False):
        magnet = magnet.strip()
        folder_name = self.sanitize_name(folder_name)
        save_dir = self.torrent_dir / folder_name
        save_dir.mkdir(parents=True, exist_ok=True)

        if not magnet.startswith("magnet:?xt=urn:btih:"):
            raise ValueError("Invalid magnet link.")

        options = self.build_torrent_options(
            private=private,
            seed=seed
        )

        gid = self.add_aria2_download([magnet], save_dir, speed_limit, options)

        print("Magnet added")
        print("Output:", save_dir)
        print("Metadata GID:", gid)
        print("Private mode:", "enabled" if private else "disabled")
        print("Seeding:", "enabled" if seed else "disabled")

        self.wait_for_torrent_metadata(gid)

        real_gid = self.find_real_torrent_gid(gid, save_dir)

        print("Starting torrent download monitor")
        print("Download GID:", real_gid)

        self.monitor_aria2(real_gid, "Torrent Download", seed=seed)

        self.save_history({
            "type": "private_torrent_magnet" if private else "torrent",
            "source": magnet,
            "output": str(save_dir),
            "status": "completed",
            "seed": seed
        })

        print("Download completed")
        print("Saved to:", save_dir)

    def download_torrent_file(self, source, folder_name="", speed_limit="", private=False, seed=False):
        source = source.strip()
        folder_name = self.sanitize_name(folder_name)
        save_dir = self.torrent_dir / folder_name
        save_dir.mkdir(parents=True, exist_ok=True)

        torrent_bytes = self.fetch_torrent_file_bytes(source)
        infohash = self.get_torrent_infohash(torrent_bytes)

        if infohash:
            print("Torrent InfoHash:", infohash)

            existing = self.find_existing_torrent_by_infohash(infohash)

            if existing:
                existing_gid = existing.get("gid")
                existing_status = existing.get("status", "unknown")

                print("This torrent is already registered in aria2")
                print("Existing GID:", existing_gid)
                print("Existing status:", existing_status)

                if existing_status == "error":
                    print("Existing torrent is in error state")
                    print("Removing old GID and adding again")
                    removed = self.remove_existing_torrent_gid(existing_gid)

                    if not removed:
                        raise RuntimeError("Could not remove existing errored torrent GID")

                else:
                    print("Using existing torrent instead of adding duplicate")
                    self.monitor_aria2(existing_gid, "Torrent Resume", seed=seed)

                    self.save_history({
                        "type": "private_torrent_file_resume" if private else "torrent_file_resume",
                        "source": source,
                        "output": str(save_dir),
                        "status": "resumed",
                        "seed": seed
                    })

                    print("Torrent handled with existing GID")
                    return

        options = self.build_torrent_options(
            private=private,
            seed=seed
        )

        try:
            gid = self.add_aria2_torrent(torrent_bytes, save_dir, speed_limit, options)
        except Exception as error:
            message = str(error)

            if "already registered" in message:
                print("This torrent is already registered in aria2.")
                print("Open Torrent Tools > aria2 status, remove the existing GID, then try again.")
                raise RuntimeError(message)

            debug_file = self.logs_dir / f"failed_torrent_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.torrent"
            debug_file.write_bytes(torrent_bytes)

            print("Failed to pass torrent data to aria2")
            print("Saved downloaded .torrent for debugging:")
            print(debug_file)

            raise error

        print("Torrent file added")
        print("Output:", save_dir)
        print("Download GID:", gid)
        print("Private mode:", "enabled" if private else "disabled")
        print("Seeding:", "enabled" if seed else "disabled")

        try:
            self.monitor_aria2(gid, "Torrent File Download", seed=seed)
        except Exception as error:
            message = str(error)

            if "already registered" in message:
                print("Duplicate torrent detected after adding")
                print("Removing duplicate GID:", gid)
                self.remove_existing_torrent_gid(gid)
                raise RuntimeError("Torrent already exists in aria2. Removed duplicate GID. Try again or use aria2 status.")

            raise error

        self.save_history({
            "type": "private_torrent_file" if private else "torrent_file",
            "source": source,
            "output": str(save_dir),
            "status": "completed",
            "seed": seed
        })

        print("Download completed")
        print("Saved to:", save_dir)

    def download_private_torrent(self):
        print("Private Torrent")
        print("-" * 80)
        print("Recommended: use a .torrent file from your private tracker.")
        print("Private mode disables DHT, DHT6, PEX, and LPD.")
        print("Seeding works only while the Colab runtime is alive.")
        print("For long-term seeding, use a seedbox or VPS.")
        print("-" * 80)

        source = input("Private .torrent URL, local path, or magnet: ").strip()
        folder_name = input("Folder name optional: ").strip()
        speed_limit = input("Speed limit optional, example 5M: ").strip()
        seed_answer = input("Keep seeding after download? y/n: ").strip().lower()
        seed = seed_answer == "y"

        if not source:
            print("No torrent source entered")
            return

        if source.startswith("magnet:?"):
            print("Warning: magnet links are not recommended for private torrents.")
            print("A .torrent file is strongly recommended for private trackers.")
            self.download_magnet(
                magnet=source,
                folder_name=folder_name,
                speed_limit=speed_limit,
                private=True,
                seed=seed
            )
            return

        self.download_torrent_file(
            source=source,
            folder_name=folder_name,
            speed_limit=speed_limit,
            private=True,
            seed=seed
        )

    def torrent_menu(self):
        while True:
            print("")
            print("=" * 70)
            print("Torrent Tools")
            print("=" * 70)
            print("1. Torrent magnet")
            print("2. Torrent file")
            print("3. Private torrent")
            print("4. aria2 status")
            print("5. Remove aria2 GID")
            print("6. Clear stopped aria2 results")
            print("7. Save aria2 session")
            print("8. Back")

            choice = input("Select torrent option: ").strip()

            try:
                if choice == "1":
                    magnet = input("Magnet link: ").strip()
                    folder_name = input("Folder name optional: ").strip()
                    speed_limit = input("Speed limit optional, example 5M: ").strip()
                    seed_answer = input("Keep seeding after download? y/n: ").strip().lower()
                    seed = seed_answer == "y"

                    self.download_magnet(
                        magnet=magnet,
                        folder_name=folder_name,
                        speed_limit=speed_limit,
                        private=False,
                        seed=seed
                    )

                elif choice == "2":
                    source = input("Torrent file URL or path: ").strip()
                    folder_name = input("Folder name optional: ").strip()
                    speed_limit = input("Speed limit optional, example 5M: ").strip()
                    seed_answer = input("Keep seeding after download? y/n: ").strip().lower()
                    seed = seed_answer == "y"

                    self.download_torrent_file(
                        source=source,
                        folder_name=folder_name,
                        speed_limit=speed_limit,
                        private=False,
                        seed=seed
                    )

                elif choice == "3":
                    self.download_private_torrent()

                elif choice == "4":
                    self.print_aria2_status()

                elif choice == "5":
                    self.remove_aria2_gid()

                elif choice == "6":
                    self.purge_aria2_stopped()

                elif choice == "7":
                    self.save_aria2_session()

                elif choice == "8":
                    break

                else:
                    print("Invalid torrent option")

            except KeyboardInterrupt:
                self.save_aria2_session()
                print("Cancelled")

            except Exception as error:
                self.save_aria2_session()
                print("Error:", error)

    def parse_headers_json(self, text):
        text = str(text or "").strip()

        if not text:
            return None

        try:
            data = json.loads(text)
        except Exception:
            print("Invalid headers JSON, ignored")
            return None

        if not isinstance(data, dict):
            print("Headers JSON must be an object, ignored")
            return None

        return data

    def download_direct(self, url, folder_name="", file_name="", speed_limit="", headers=None):
        url = url.strip()
        folder_name = self.sanitize_name(folder_name)
        file_name = file_name.strip()
        save_dir = self.direct_dir / folder_name
        save_dir.mkdir(parents=True, exist_ok=True)

        if not url.startswith(("http://", "https://", "ftp://")):
            raise ValueError("Invalid direct link.")

        options = {}

        if file_name:
            options["out"] = self.sanitize_name(file_name)

        if headers:
            header_lines = []

            for key, value in headers.items():
                if key and value:
                    header_lines.append(f"{key}: {value}")

            if header_lines:
                options["header"] = header_lines

        gid = self.add_aria2_download([url], save_dir, speed_limit, options)

        print("Direct download added")
        print("Output:", save_dir)

        self.monitor_aria2(gid, "Direct")

        self.save_history({
            "type": "direct",
            "source": url,
            "output": str(save_dir),
            "status": "completed"
        })

        print("Download completed")
        print("Saved to:", save_dir)

    # ─────────────────────────────────────────────────────────────────────────
    # YouTube
    # ─────────────────────────────────────────────────────────────────────────

    def get_youtube_available_qualities(self, url):
        """
        Fetch video info once and return only the quality levels that actually
        exist as video streams, plus always "best" as first option.
        Returns (qualities_list, info_dict).
        """
        with YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get("formats", [])
        standard_heights = [4320, 2160, 1440, 1080, 720, 480, 360, 240, 144]

        available_heights = set()
        for f in formats:
            h = f.get("height")
            vcodec = f.get("vcodec", "none")
            if h and vcodec and vcodec != "none":
                available_heights.add(int(h))

        qualities = ["best"]
        for h in standard_heights:
            if h in available_heights:
                qualities.append(str(h))

        return qualities, info

    def select_youtube_quality(self, url):
        """
        Fetch video info, ask audio/video preference, then show only the
        quality options the video actually has.
        Returns (quality_string, audio_only_bool).
        """
        print("Fetching video info...")

        try:
            qualities, info = self.get_youtube_available_qualities(url)
        except Exception as error:
            print("Could not fetch video info:", error)
            print("Falling back to best quality")
            return "best", False

        title = info.get("title", "")
        duration = info.get("duration", 0)
        uploader = info.get("uploader", "")

        print("-" * 60)
        if title:
            print("Title   :", title)
        if uploader:
            print("Channel :", uploader)
        if duration:
            print("Duration:", self.format_seconds(int(duration)))
        print("-" * 60)

        audio_answer = input("Audio only? y/n: ").strip().lower()
        if audio_answer == "y":
            return "best", True

        print("Available qualities:")
        for i, q in enumerate(qualities, 1):
            label = "Best available" if q == "best" else f"{q}p"
            print(f"  {i}. {label}")

        choice = input(f"Select quality (1-{len(qualities)}, default 1): ").strip()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(qualities):
                selected = qualities[idx]
                label = "Best available" if selected == "best" else f"{selected}p"
                print("Selected:", label)
                return selected, False

        print("Invalid selection, using best quality")
        return "best", False

    def build_youtube_format(self, quality, audio_only):
        """
        Build a yt-dlp format string.
        For video downloads, audio is always merged — no silent video possible.
        """
        quality = str(quality or "best").strip().lower()

        if audio_only:
            return "bestaudio/best"

        if quality == "best":
            return "bv*[vcodec!=none]+ba/bestvideo+bestaudio/best"

        if quality in ["4320", "2160", "1440", "1080", "720", "480", "360", "240", "144"]:
            return (
                f"bestvideo[height={quality}][vcodec!=none]+bestaudio/"
                f"bestvideo[height<={quality}][vcodec!=none]+bestaudio/"
                f"best[height<={quality}]/best"
            )

        return "bv*[vcodec!=none]+ba/bestvideo+bestaudio/best"

    def download_youtube(self, url, folder_name="", quality="best", audio_only=False, playlist=True, metadata=False):
        url = url.strip()
        folder_name = self.sanitize_name(folder_name)
        save_dir = self.youtube_dir / folder_name
        save_dir.mkdir(parents=True, exist_ok=True)

        progress_state = {
            "bar": None,
            "last": 0
        }

        def hook(data):
            if data.get("status") == "downloading":
                total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
                downloaded = data.get("downloaded_bytes") or 0
                speed = data.get("speed") or 0

                if total and progress_state["bar"] is None:
                    progress_state["bar"] = tqdm(
                        total=total,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc="YouTube"
                    )

                if progress_state["bar"]:
                    delta = downloaded - progress_state["last"]

                    if delta > 0:
                        progress_state["bar"].update(delta)

                    progress_state["bar"].set_postfix({
                        "speed": self.format_bytes(speed) + "/s"
                    })

                progress_state["last"] = downloaded

            elif data.get("status") == "finished":
                if progress_state["bar"]:
                    progress_state["bar"].close()
                    progress_state["bar"] = None

                progress_state["last"] = 0
                print("Processing file")

        selected_format = self.build_youtube_format(quality, audio_only)

        if audio_only:
            postprocessors = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320"
                }
            ]
        else:
            postprocessors = [
                {
                    "key": "FFmpegMetadata"
                }
            ]

        options = {
            "format": selected_format,
            "outtmpl": str(save_dir / "%(playlist_index|)s%(playlist_index& - |)s%(title).200s.%(ext)s"),
            "merge_output_format": "mp4",
            "noplaylist": not playlist,
            "ignoreerrors": False,
            "continuedl": True,
            "retries": 10,
            "fragment_retries": 10,
            "concurrent_fragment_downloads": 4,
            "progress_hooks": [hook],
            "postprocessors": postprocessors,
            "quiet": True,
            "no_warnings": True,
            "writeinfojson": metadata,
            "writethumbnail": metadata
        }

        print("YouTube download started")
        print("Format:", selected_format)
        print("Output:", save_dir)

        with YoutubeDL(options) as ydl:
            ydl.download([url])

        self.save_history({
            "type": "youtube",
            "source": url,
            "output": str(save_dir),
            "format": selected_format,
            "status": "completed"
        })

        print("Download completed")
        print("Saved to:", save_dir)

    # ─────────────────────────────────────────────────────────────────────────

    def auto_download(self, value):
        link_type = self.detect_link_type(value)

        if link_type == "unknown":
            raise ValueError("Unknown link type.")

        print("Detected:", link_type)

        folder_name = input("Folder name optional: ").strip()

        if link_type == "torrent":
            speed_limit = input("Speed limit optional, example 5M: ").strip()
            seed_answer = input("Keep seeding after download? y/n: ").strip().lower()
            seed = seed_answer == "y"

            self.download_magnet(
                value,
                folder_name,
                speed_limit,
                private=False,
                seed=seed
            )

        elif link_type == "torrent_file":
            speed_limit = input("Speed limit optional, example 5M: ").strip()
            seed_answer = input("Keep seeding after download? y/n: ").strip().lower()
            seed = seed_answer == "y"

            self.download_torrent_file(
                value,
                folder_name,
                speed_limit,
                private=False,
                seed=seed
            )

        elif link_type == "youtube":
            quality, audio_only = self.select_youtube_quality(value)
            playlist_answer = input("Download playlist if detected? y/n: ").strip().lower()
            playlist = playlist_answer != "n"
            metadata_answer = input("Save YouTube metadata and thumbnail? y/n: ").strip().lower()
            metadata = metadata_answer == "y"

            self.download_youtube(
                url=value,
                folder_name=folder_name,
                quality=quality,
                audio_only=audio_only,
                playlist=playlist,
                metadata=metadata
            )

        elif link_type == "direct":
            file_name = input("File name optional: ").strip()
            speed_limit = input("Speed limit optional, example 5M: ").strip()
            headers_text = input('Headers JSON optional, example {"User-Agent":"Mozilla/5.0"}: ').strip()
            headers = self.parse_headers_json(headers_text)
            self.download_direct(value, folder_name, file_name, speed_limit, headers)

    def batch_download(self):
        print("Enter links one by one")
        print("Submit an empty line to start")

        links = []

        while True:
            value = input("Link: ").strip()

            if not value:
                break

            links.append(value)

        if not links:
            print("No links entered")
            return

        folder_name = input("Batch folder name optional: ").strip()
        folder_name = self.sanitize_name(folder_name)
        speed_limit = input("Speed limit for direct and torrent optional, example 5M: ").strip()

        for index, link in enumerate(links, 1):
            print("")
            print("=" * 80)
            print("Item:", index, "of", len(links))
            print("Link:", link)

            link_type = self.detect_link_type(link)
            batch_folder = f"{folder_name}_{index}"

            try:
                if link_type == "torrent":
                    self.download_magnet(link, batch_folder, speed_limit, private=False, seed=False)

                elif link_type == "torrent_file":
                    self.download_torrent_file(link, batch_folder, speed_limit, private=False, seed=False)

                elif link_type == "youtube":
                    self.download_youtube(
                        url=link,
                        folder_name=batch_folder,
                        quality="best",
                        audio_only=False,
                        playlist=True,
                        metadata=False
                    )

                elif link_type == "direct":
                    self.download_direct(link, batch_folder, "", speed_limit)

                else:
                    print("Skipped unknown link")

            except Exception as error:
                print("Failed:", error)

                self.save_history({
                    "type": link_type,
                    "source": link,
                    "output": batch_folder,
                    "status": "failed",
                    "error": str(error)
                })

    def storage_report(self):
        total, used, free = shutil.disk_usage(str(self.my_drive_path))

        print("Google Drive mount storage")
        print("-" * 80)
        print("Total:", self.format_bytes(total))
        print("Used:", self.format_bytes(used))
        print("Free:", self.format_bytes(free))

        print("")
        print("Project folders")
        print("-" * 80)

        folders = [
            self.torrent_dir,
            self.youtube_dir,
            self.direct_dir,
            self.batch_dir,
            self.archive_dir,
            self.logs_dir
        ]

        for folder in folders:
            print(self.format_bytes(self.folder_size(folder)), folder)

    def folder_size(self, folder):
        folder = Path(folder)

        if not folder.exists():
            return 0

        total = 0

        for item in folder.glob("**/*"):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except Exception:
                    pass

        return total

    def sha256_file(self, file_path):
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        if not file_path.is_file():
            raise ValueError("Path is not a file")

        h = hashlib.sha256()
        total = file_path.stat().st_size

        with file_path.open("rb") as f, tqdm(total=total, unit="B", unit_scale=True, unit_divisor=1024, desc="SHA256") as bar:
            while True:
                chunk = f.read(1 * 1024 * 1024)

                if not chunk:
                    break

                h.update(chunk)
                bar.update(len(chunk))

        return h.hexdigest()

    def hash_latest_file(self):
        latest = self.get_latest_file()

        if not latest:
            print("No files found")
            return

        print("Latest file:", latest)
        print("Size:", self.format_bytes(latest.stat().st_size))

        digest = self.sha256_file(latest)

        print("SHA256:")
        print(digest)

    def sha256_selected_file(self):
        file_path = self.select_file()

        if not file_path:
            return

        digest = self.sha256_file(file_path)

        print("File:", file_path)
        print("SHA256:", digest)

    def zip_folder(self):
        source = input("Folder path to zip: ").strip()

        if not source:
            print("No folder path entered")
            return

        source_path = Path(source)

        if not source_path.exists():
            print("Folder does not exist")
            return

        if not source_path.is_dir():
            print("Path is not a folder")
            return

        output_name = input("Output zip name optional: ").strip()

        if not output_name:
            output_name = source_path.name + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        output_name = self.sanitize_name(output_name)


        local_base = Path("/content") / output_name
        final_dest = self.archive_dir / f"{output_name}.zip"

        print("Creating ZIP locally on fast SSD...")
        local_result = shutil.make_archive(str(local_base), "zip", str(source_path))

        print("Moving final ZIP to Google Drive...")
        shutil.move(local_result, str(final_dest))

        print("ZIP created and moved to:")
        print(str(final_dest))

        self.save_history({
            "type": "zip",
            "source": str(source_path),
            "output": str(final_dest),
            "status": "completed"
        })

    def zip_latest_folder(self):
        latest_folder = self.get_latest_downloaded_folder()

        if not latest_folder:
            print("No folders found")
            return

        print("Latest folder:")
        print(latest_folder)

        confirm = input("Zip this folder? y/n: ").strip().lower()

        if confirm != "y":
            print("Cancelled")
            return

        output_name = latest_folder.name + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_name = self.sanitize_name(output_name)

        local_base = Path("/content") / output_name
        final_dest = self.archive_dir / f"{output_name}.zip"

        print("Creating ZIP locally on fast SSD...")
        local_result = shutil.make_archive(str(local_base), "zip", str(latest_folder))

        print("Moving final ZIP to Google Drive...")
        shutil.move(local_result, str(final_dest))

        print("ZIP created and moved to:")
        print(str(final_dest))

        self.save_history({
            "type": "zip",
            "source": str(latest_folder),
            "output": str(final_dest),
            "status": "completed"
        })

    def print_developer(self):
        text = """
Developer

Project:
AzuDl - GC2GD

Full Name:
Azizi Universal Downloader - Google Colab to Google Drive

Developer:
The Azizi

X:
https://x.com/the_azzi

GitHub:
https://github.com/TheGreatAzizi

Telegram:
https://t.me/luluch_code

Git:
https://git.theazizi.ir/TheAzizi

Website:
https://theazizi.ir
"""
        print(text.strip())

    def print_help(self):
        text = """
AzuDl - GC2GD Help

Project:
AzuDl - GC2GD

Full Name:
Azizi Universal Downloader - Google Colab to Google Drive

Main options:
1. Auto detect link
2. Torrent tools
3. YouTube video or playlist
4. Direct link
5. Batch download
6. Download history
7. List downloaded files
8. Storage report
9. SHA256 latest file
10. SHA256 selected file
11. ZIP folder
12. ZIP latest folder
13. Latest file
14. Developer
15. Help
16. Exit

Torrent tools:
1. Torrent magnet
2. Torrent file
3. Private torrent
4. aria2 status
5. Remove aria2 GID
6. Clear stopped aria2 results
7. Save aria2 session
8. Back

YouTube quality selection:
AzuDl fetches video info before asking quality.
Only qualities that actually exist in the video are shown.
Audio is always merged into the video — silent downloads are not possible.
For audio-only downloads, the output is saved as MP3 at 320kbps.

Resume support:
AzuDl uses aria2 session persistence.
Session file:
/content/drive/MyDrive/AzuDl-GC2GD/Logs/aria2.session

Duplicate torrent handling:
AzuDl reads torrent InfoHash before adding .torrent files.
If the same torrent already exists in aria2, it resumes or monitors the existing GID instead of adding a duplicate.
If the existing torrent is in error state, AzuDl removes it and adds the torrent again.

Google Colab may disconnect idle or long-running sessions.
AzuDl does not bypass Colab timeout.
After reconnecting, run the notebook again and check aria2 status.

Private torrent:
Use this option for private tracker torrents.
Using a .torrent file is strongly recommended.
Private mode disables DHT, DHT6, PEX, and LPD.
If seeding is enabled, aria2 keeps seeding while the Colab runtime is alive.
Google Colab is not suitable for permanent seeding.
For long-term seeding, use a seedbox or VPS.

Torrent seeding:
AzuDl uses 525600 minutes when seeding is enabled.
Live seeding status shows upload speed, uploaded size, ratio, connections, seeders, and elapsed time.

Direct headers:
You can pass optional headers as JSON.
Example:
{"User-Agent":"Mozilla/5.0","Referer":"https://example.com"}

Speed limit examples:
500K
2M
10M

Notes:
Use only content you have the right to download.
Private torrent seeding stops when Colab runtime disconnects.
"""
        print(text.strip())


def main():
    app = AzuDlGC2GD()

    try:
        app.setup()
    except Exception as error:
        print("Startup failed:", error)
        return

    while True:
        print("")
        print("=" * 70)
        print(app.project_name)
        print("=" * 70)
        print("1. Auto detect link")
        print("2. Torrent tools")
        print("3. YouTube video or playlist")
        print("4. Direct link")
        print("5. Batch download")
        print("6. Download history")
        print("7. List downloaded files")
        print("8. Storage report")
        print("9. SHA256 latest file")
        print("10. SHA256 selected file")
        print("11. ZIP folder")
        print("12. ZIP latest folder")
        print("13. Latest file")
        print("14. Developer")
        print("15. Help")
        print("16. Exit")

        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                value = input("Link: ").strip()
                app.auto_download(value)

            elif choice == "2":
                app.torrent_menu()

            elif choice == "3":
                url = input("YouTube URL: ").strip()
                folder_name = input("Folder name optional: ").strip()
                quality, audio_only = app.select_youtube_quality(url)
                playlist_answer = input("Download playlist if detected? y/n: ").strip().lower()
                playlist = playlist_answer != "n"
                metadata_answer = input("Save metadata and thumbnail? y/n: ").strip().lower()
                metadata = metadata_answer == "y"

                app.download_youtube(
                    url=url,
                    folder_name=folder_name,
                    quality=quality,
                    audio_only=audio_only,
                    playlist=playlist,
                    metadata=metadata
                )

            elif choice == "4":
                url = input("Direct URL: ").strip()
                folder_name = input("Folder name optional: ").strip()
                file_name = input("File name optional: ").strip()
                speed_limit = input("Speed limit optional, example 5M: ").strip()
                headers_text = input('Headers JSON optional, example {"User-Agent":"Mozilla/5.0"}: ').strip()
                headers = app.parse_headers_json(headers_text)
                app.download_direct(url, folder_name, file_name, speed_limit, headers)

            elif choice == "5":
                app.batch_download()

            elif choice == "6":
                app.print_history()

            elif choice == "7":
                app.list_downloads()

            elif choice == "8":
                app.storage_report()

            elif choice == "9":
                app.hash_latest_file()

            elif choice == "10":
                app.sha256_selected_file()

            elif choice == "11":
                app.zip_folder()

            elif choice == "12":
                app.zip_latest_folder()

            elif choice == "13":
                app.print_latest_file()

            elif choice == "14":
                app.print_developer()

            elif choice == "15":
                app.print_help()

            elif choice == "16":
                app.save_aria2_session()
                print("Exit")
                break

            else:
                print("Invalid option")

        except KeyboardInterrupt:
            app.save_aria2_session()
            print("Cancelled")

        except Exception as error:
            app.save_aria2_session()
            print("Error:", error)


main()
