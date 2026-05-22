# =========================
# INSTALL
# =========================
!apt update -qq
!apt install -y aria2 ffmpeg p7zip-full
!pip install -q tqdm requests yt-dlp

# =========================
# IMPORTS
# =========================
import re
import json
import time
import socket
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

import requests
from tqdm.notebook import tqdm
from yt_dlp import YoutubeDL
from google.colab import drive


# =========================
# MAIN CLASS
# =========================
class AzuDlGC2GD:

    def __init__(self):

        self.base = Path("/content/drive/MyDrive/AzuDl-GC2GD")

        self.torrent_dir = self.base / "Torrent"
        self.youtube_dir = self.base / "YouTube"
        self.direct_dir = self.base / "Direct"
        self.logs_dir = self.base / "Logs"

        self.history_file = self.logs_dir / "history.json"

        self.rpc_url = "http://127.0.0.1:6800/jsonrpc"


    # =========================
    # SETUP
    # =========================
    def setup(self):
        drive.mount("/content/drive")
        print("✅ Drive mounted")

        for d in [self.torrent_dir, self.youtube_dir, self.direct_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.start_aria2()


    # =========================
    # ARIA2 FIXED
    # =========================
    def is_port_open(self):
        with socket.socket() as s:
            s.settimeout(1)
            return s.connect_ex(("127.0.0.1", 6800)) == 0


    def start_aria2(self):

        if self.is_port_open():
            print("✅ aria2 already running")
            return

        cmd = [
            "aria2c",
            "--enable-rpc=true",
            "--rpc-listen-all=false",
            "--rpc-listen-port=6800",
            "--rpc-allow-origin-all=true",
            "--daemon=true",
            "--file-allocation=none",
            "--continue=true",
            "--max-tries=0",
            "--retry-wait=5",
            "--timeout=60",
            "--connect-timeout=60",
            "--enable-dht=true",
            "--bt-enable-lpd=true",
            "--bt-save-metadata=true",
            "--console-log-level=warn"
        ]

        subprocess.run(cmd, check=True)

        for _ in range(20):
            if self.is_port_open():
                print("✅ aria2 started")
                return
            time.sleep(0.5)

        raise RuntimeError("aria2 failed")


    # =========================
    # RPC
    # =========================
    def rpc(self, method, params=None):

        r = requests.post(
            self.rpc_url,
            json={
                "jsonrpc": "2.0",
                "id": "azu",
                "method": method,
                "params": params or []
            },
            timeout=20
        )

        r.raise_for_status()

        data = r.json()

        if "error" in data:
            raise RuntimeError(data["error"])

        return data["result"]


    # =========================
    # HELPERS
    # =========================
    def sanitize(self, name):

        if not name:
            return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        name = re.sub(r'[\\/:*?"<>|]', "_", name)
        return name.strip()


    def save_history(self, item):

        self.logs_dir.mkdir(exist_ok=True)

        history = []

        if self.history_file.exists():
            try:
                history = json.loads(self.history_file.read_text())
            except:
                history = []

        item["time"] = str(datetime.now())
        history.append(item)

        self.history_file.write_text(json.dumps(history, indent=2))


    # =========================
    # SAFE DOWNLOAD (FIX)
    # =========================
    def safe_request(self, url):

        return requests.get(
            url,
            timeout=60,
            verify=False,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        )


    # =========================
    # ARIA2 DOWNLOAD
    # =========================
    def aria2_download(self, url, folder):

        options = {
            "dir": str(folder),
            "continue": "true",
            "file-allocation": "none"
        }

        return self.rpc("aria2.addUri", [[url], options])


    def monitor(self, gid):

        last = 0
        bar = None

        while True:

            s = self.rpc("aria2.tellStatus", [gid])

            total = int(s.get("totalLength", 0))
            done = int(s.get("completedLength", 0))
            speed = int(s.get("downloadSpeed", 0))
            status = s.get("status")

            if status == "error":
                raise RuntimeError(s.get("errorMessage"))

            if total > 0 and not bar:
                bar = tqdm(total=total, unit="B", unit_scale=True)

            if bar:
                bar.update(done - last)
                bar.set_postfix(speed=f"{speed//1024} KB/s")

            last = done

            if status == "complete":
                if bar:
                    bar.close()
                return

            time.sleep(1)


    # =========================
    # DIRECT DOWNLOAD (FIXED LOGIC)
    # =========================
    def download_direct(self, url):

        folder = self.direct_dir / self.sanitize("Direct")
        folder.mkdir(parents=True, exist_ok=True)

        print("⬇️ Download started")

        try:
            gid = self.aria2_download(url, folder)
            self.monitor(gid)

        except Exception as e:
            print("⚠️ aria2 failed, fallback mode:", e)

            r = self.safe_request(url)

            filename = url.split("/")[-1].split("?")[0] or "file.bin"

            path = folder / filename

            path.write_bytes(r.content)

            print("✅ fallback saved:", path)

        self.save_history({
            "type": "direct",
            "source": url,
            "output": str(folder),
            "status": "done"
        })


    # =========================
    # MENU
    # =========================
    def run(self):

        while True:

            print("\n=== AZU DL ===")
            print("1. Auto detect")
            print("2. Direct")
            print("3. Exit")

            c = input("Select: ").strip()

            if c == "1":

                url = input("Link: ").strip()

                self.download_direct(url)

            elif c == "2":

                url = input("Direct URL: ").strip()

                self.download_direct(url)

            elif c == "3":

                break


# =========================
# RUN
# =========================
app = AzuDlGC2GD()
app.setup()
app.run()