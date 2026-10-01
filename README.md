# AzuDl - GC2GD
[![DevSponsors](https://devsponsors.github.io/assets/badges/sponsor.svg)](https://devsponsors.github.io)
**Azizi Universal Downloader - Google Colab to Google Drive**

AzuDl - GC2GD is a Google Colab based universal downloader that downloads supported files directly to Google Drive. It supports direct links, YouTube videos and playlists, torrent magnet links, `.torrent` files, private torrent mode, batch downloads, download history, file management tools, ZIP creation, SHA256 hashing, aria2 status monitoring, duplicate torrent detection, live seeding status, resumable downloads using aria2 session persistence, and a Colab GUI beta interface.

> فارسی: [README.fa.md](README.fa.md)

---

## Version

```text
Version: 1.4.20 GUI Beta
```

---

## Features

- GitHub repository downloader
- Official project repository downloader
- GitHub token field and rate-limit status
- Specific GitHub release tag download
- GitHub release assets and source archive download
- GitHub README and license download options
- Verified Google Drive transfer workflow
- Force Drive sync tool
- System diagnostic tool
- Mobile-friendly GUI tabs
- Improved role-based button colors
- Colab GUI beta interface
- Tab-based dashboard
- Direct link download to Google Drive
- YouTube video download
- YouTube playlist download
- YouTube quality selection
- YouTube audio-only MP3 extraction
- Custom YouTube format ID support
- Auto-fix for video-only YouTube formats by adding best available audio
- Magnet torrent download
- `.torrent` file download from URL or local path
- Private torrent mode
- Optional torrent seeding after download
- Live torrent download progress
- Live torrent seeding status
- Upload speed display during seeding
- Uploaded size display during seeding
- Torrent ratio display
- Seeder and connection display
- Duplicate torrent InfoHash detection
- Resume existing aria2 torrent tasks instead of adding duplicates
- Remove errored duplicate torrents automatically
- aria2 session persistence
- Resume-friendly download behavior
- Auto link type detection
- Batch download
- Download history
- List downloaded files
- Latest file viewer
- Google Drive storage report
- SHA256 hash for latest or selected files
- ZIP selected folder
- ZIP latest downloaded folder
- Dedicated Torrent Tools menu
- Developer information section
- Built-in help menu

---

## <img src="https://img.shields.io/badge/v1.4.20-GUI%20Beta-5865F2?style=for-the-badge" alt="1.4.20 GUI Beta">

> [!IMPORTANT]
> `1.4.20 GUI Beta` introduces the first Colab graphical interface for **AzuDl - GC2GD**.  
> The classic CLI is still available, but the default experience is now the GUI.

<details>
<summary><strong>What is new in 1.4.20 GUI Beta?</strong></summary>

<br>

Version `1.4.20 GUI Beta` adds a new Google Colab widget-based graphical interface for AzuDl - GC2GD.

This beta release keeps the original CLI workflow available, but adds a tab-based GUI for users who prefer buttons, forms, dropdowns, checkboxes, and visual controls instead of typing menu numbers.

The GUI is designed to make AzuDl easier to use for public GitHub users, especially new users who want to download direct links, YouTube videos, torrents, batch links, manage files, check storage, and access help tools from one interface.

</details>

<details>
<summary><strong>GUI Highlights</strong></summary>

<br>

| Area | Added in GUI Beta |
|---|---|
| Interface | Colab widget-based graphical interface |
| Navigation | Tab-based layout |
| Dashboard | Quick access to status, storage, history, and files |
| Auto Download | Auto-detect direct, YouTube, magnet, and torrent links |
| Direct | Custom file name, folder, headers, and speed limit |
| YouTube | Quality selection, audio-only mode, playlist mode, metadata |
| Torrent | Magnet, `.torrent`, private mode, seeding, aria2 status |
| Batch | Multiple links, one per line |
| Files | List files, latest file, SHA256 tools |
| Archives | ZIP folder and ZIP latest folder |
| Maintenance | Save session, clear stopped tasks, remove GID |
| Developer | Project and developer links |
| Guide | Help, cookie help, and PO Token help |

</details>

<details>
<summary><strong>Default Interface</strong></summary>

<br>

Starting from `1.4.20 GUI Beta`, the default interface is the GUI.

When the notebook cell is run normally, AzuDl launches the Colab GUI automatically:

```python
launch_gui()
```

The classic CLI is still available:

```python
main()
```

You can also force CLI mode before running the script:

```python
import os
os.environ["AZUDL_INTERFACE"] = "cli"
```

</details>

<details>
<summary><strong>GUI Tabs</strong></summary>

<br>

```text
Dashboard
Auto
Direct
YouTube
Auth
Torrent
Batch
GitHub
Official
Files
Archives
Maintenance
Developer
Guide
```

</details>

<details>
<summary><strong>Beta Notes</strong></summary>

<br>

This is a beta GUI release. The download engine is still based on the same AzuDl core features, including aria2, yt-dlp, Google Drive storage, history, ZIP tools, SHA256 tools, and aria2 session persistence.

The GUI may receive visual improvements, layout changes, and usability updates in future versions.

</details>

<details>
<summary><strong>Suggested Commit Message</strong></summary>

<br>

```text
release: AzuDl GC2GD 1.4.20 GUI Beta
```

Alternative:

```text
feat(gui): add GitHub downloader diagnostics and verified Drive transfer
```

</details>

---

## Main Menu

```text
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
17. Launch Colab GUI
```

---

## Torrent Tools Menu

```text
1. Torrent magnet
2. Torrent file
3. Private torrent
4. aria2 status
5. Remove aria2 GID
6. Clear stopped aria2 results
7. Save aria2 session
8. Back
```

---

## GUI Tabs

The GUI beta provides the following tabs inside Google Colab:

```text
Dashboard
Auto
Direct
YouTube
Auth
Torrent
Batch
GitHub
Official
Files
Archives
Maintenance
Developer
Guide
```

| Tab | Purpose |
|---|---|
| Dashboard | Quick access to status, storage, history, and file tools |
| Auto | Detect link type and download supported links |
| Direct | Download direct HTTP, HTTPS, or FTP links |
| YouTube | Download YouTube videos, playlists, audio, metadata, and thumbnails |
| Torrent | Download magnets, `.torrent` files, private torrents, and manage seeding |
| Batch | Download multiple links one by one |
| Files | List downloads, view latest file, and calculate SHA256 |
| Archives | Create ZIP archives |
| GitHub | Download public or private GitHub repository releases, assets, source archives, README, and license files |
| Official | Download the official AzuDl project repository without entering the URL manually |
| Maintenance | Save aria2 session, remove GID, clear stopped tasks, force Drive sync, run diagnostics, and check storage |
| Developer | Show project and developer links |
| Guide | Show help, cookie help, and PO Token help |

---

## Storage Structure

AzuDl creates the following folder structure in Google Drive:

```text
/content/drive/MyDrive/AzuDl-GC2GD
```

```text
AzuDl-GC2GD/
├── TorrentDownloads/
├── YouTubeDownloads/
├── DirectDownloads/
├── BatchDownloads/
├── GitHubDownloads/
├── Archives/
└── Logs/
```

| Folder | Purpose |
|---|---|
| `TorrentDownloads` | Torrent magnet and `.torrent` downloads |
| `YouTubeDownloads` | YouTube video, playlist, and audio downloads |
| `DirectDownloads` | Direct URL downloads |
| `BatchDownloads` | Batch download outputs |
| `GitHubDownloads` | GitHub repository, release, asset, and official project downloads |
| `Archives` | ZIP files created by AzuDl |
| `Logs` | History, aria2 session file, cookies templates, token templates, and debug files |

---


---

## GitHub Repository Downloader

The GitHub tab can fetch repository information and download files directly to Google Drive.

Supported repository input:

```text
https://github.com/owner/repository
```

Supported download modes:

| Mode | Description |
|---|---|
| Latest release | Downloads assets and optional source archives from the newest release |
| Specific release tag | Downloads assets and optional source archives from a selected tag |
| All releases | Downloads assets and optional source archives from all returned releases |
| Default branch source | Downloads the default branch ZIP archive |

Optional GitHub downloads:

- Release assets
- Source ZIP/TAR archives
- README
- License candidates

For private repositories or higher API limits, paste a GitHub token in the GitHub tab and click **Save token**.

AzuDl stores the optional token template at:

```text
/content/drive/MyDrive/AzuDl-GC2GD/Logs/github_token.txt
```

Environment variable alternative:

```text
AZUDL_GITHUB_TOKEN
```

Never share or commit a real GitHub token.

---

## Official Project Repository

The Official tab is dedicated to the AzuDl project repository:

```text
https://github.com/TheGreatAzizi/AzuDL-GC2GD
```

It can download official releases, release assets, source archives, README, license files, or the default branch source ZIP.

If no release asset is available, AzuDl can fall back to the default branch source ZIP.

---

## System Diagnostic

The Maintenance tab includes **Run diagnostic**.

It checks:

- Direct download access
- GitHub API access
- YouTube metadata access
- aria2 torrent engine startup

This is useful after launching a fresh Colab runtime to confirm that the main engines are working before testing downloads manually.

---

## Google Drive Transfer Verification

AzuDl uses verified transfer logic for files that are processed locally before being saved to Google Drive.

The workflow includes:

1. Download or process files in local Colab temporary storage when needed.
2. Copy files to Google Drive in chunks.
3. Flush and `fsync` the written file.
4. Run a system sync.
5. Re-open and verify the final file on the mounted Drive path.

If the Google Drive web or mobile app does not show the file immediately, refresh Drive or wait for sync. The Maintenance tab includes **Force Drive sync**.

## aria2 Session File

AzuDl stores aria2 session data here:

```text
/content/drive/MyDrive/AzuDl-GC2GD/Logs/aria2.session
download_history.json
```

This file helps aria2 reload unfinished tasks after restarting the notebook.

AzuDl uses:

```text
--continue=true
--always-resume=true
--save-session
--input-file
--force-save=true
```

This makes downloads more resume-friendly.

---

## Important Note About Google Colab Timeout

AzuDl does not bypass Google Colab timeout. Google Colab may disconnect idle or long-running sessions depending on its runtime policies.

AzuDl improves reliability by saving aria2 session data, saving files directly to Google Drive, enabling resume options in aria2, detecting existing torrent tasks, and continuing existing aria2 jobs where possible.

For long-term torrent seeding or unattended downloading, use a VPS or seedbox.

---

## Supported Link Types

AzuDl can automatically detect:

```text
magnet:?...
https://example.com/file.zip
https://example.com/file.torrent
https://youtube.com/...
https://youtu.be/...
```

| Type | Supported |
|---|---|
| Direct HTTP/HTTPS links | Yes |
| FTP links | Yes |
| YouTube videos | Yes |
| YouTube playlists | Yes |
| Magnet links | Yes |
| `.torrent` URLs | Yes |
| Local `.torrent` files | Yes |
| Batch links | Yes |

---

## Direct Downloads

AzuDl can download direct links using aria2.

Examples:

```text
https://example.com/file.zip
https://example.com/video.mp4
https://example.com/archive.rar
https://example.com/document.pdf
```

Optional fields:

- Folder name
- Output file name
- Speed limit
- Custom headers as JSON

Example custom headers:

```json
{"User-Agent":"Mozilla/5.0","Referer":"https://example.com"}
```

---

## YouTube Downloads

AzuDl uses `yt-dlp` to download YouTube videos and playlists.

Supported options:

- Best quality
- Quality selection
- Audio-only MP3
- Playlist download
- Metadata saving
- Thumbnail saving
- Cookie file support
- PO Token support

Available quality values:

```text
best
4320
2160
1440
1080
720
480
360
240
144
```

---

## YouTube Cookies

Some YouTube downloads may fail in Colab with authentication, age restriction, or bot-check messages.

Recommended fix:

Use a Netscape-format `cookies.txt` file exported from your own logged-in browser session.

Accepted cookie paths:

```text
/content/cookies.txt
/content/youtube_cookies.txt
/content/drive/MyDrive/AzuDl-GC2GD/Logs/youtube_cookies.txt
/content/drive/MyDrive/AzuDl-GC2GD/youtube_cookies.txt
/content/drive/MyDrive/AzuDl-GC2GD/cookies.txt
```

Environment variable alternative:

```text
AZUDL_YOUTUBE_COOKIES=/path/to/cookies.txt
```

Cookie safety:

```text
Never publish, share, or commit real cookies to GitHub.
```

---

## YouTube PO Token

PO Token means Proof Of Origin Token. It is an advanced `yt-dlp` option for YouTube clients and should be used only when anonymous access and `cookies.txt` both fail.

AzuDl reads PO Token values from:

```text
/content/drive/MyDrive/AzuDl-GC2GD/Logs/youtube_po_token.txt
```

Recommended token line format:

```text
mweb+YOUR_PO_TOKEN
```

Optional Visitor Data path:

```text
/content/drive/MyDrive/AzuDl-GC2GD/Logs/youtube_visitor_data.txt
```

Environment variables also work:

```text
AZUDL_YOUTUBE_PO_TOKEN
AZUDL_YOUTUBE_VISITOR_DATA
AZUDL_YOUTUBE_PLAYER_CLIENT
```

---

## YouTube Audio Fix

Some YouTube formats are video-only, especially high quality formats.

For example:

```text
137
```

is often a video-only format.

AzuDl automatically tries to add the best available audio:

```text
137 -> 137+ba/best
```

Recommended custom format examples:

```text
137+140
248+251
22
18
best
```

---

## MP3 Audio Extraction

Choose audio-only mode to extract audio as:

```text
MP3 320kbps
```

---

## Torrent Downloads

AzuDl supports magnet links, `.torrent` file URLs, local `.torrent` files, private torrent mode, optional seeding, live download progress, live seeding status, duplicate InfoHash handling, and aria2 resume/session persistence.

### Magnet example

```text
magnet:?xt=urn:btih:EXAMPLE_HASH
```

Use:

```text
Torrent Tools > Torrent magnet
```

### Torrent file example

```text
https://example.com/file.torrent
```

Use:

```text
Torrent Tools > Torrent file
```

For public torrents, use `Torrent file`, not `Private torrent`.

---

## Private Torrent Mode

Private torrent mode is designed for private trackers.

Use:

```text
Torrent Tools > Private torrent
```

Recommended input:

```text
.torrent file from your private tracker
```

Private mode disables:

```text
DHT
DHT6
PEX
LPD
```

This is important for private trackers because many private trackers do not allow public peer discovery.

---

## Seeding

When AzuDl asks:

```text
Keep seeding after download? y/n
```

Choose:

```text
y
```

to keep seeding after the download completes.

AzuDl displays live seeding information:

```text
Upload speed
Uploaded size
Ratio
Connections
Seeders
Elapsed seeding time
```

Example:

```text
Seeding Upload: up=1.20 MB/s, uploaded=350.40 MB, ratio=0.42, connections=8, seeders=12, time=08:31
```

Seeding only works while the Colab runtime is alive. For long-term seeding, use a VPS, seedbox, or dedicated server.

---

## Why AzuDl Uses 525600 Minutes for Seeding

Some aria2 builds do not accept:

```text
seed-time=-1
```

So AzuDl uses:

```text
525600
```

This means 525600 minutes, which is around one year. Since Colab will disconnect much earlier than that, this effectively means: seed as long as the Colab runtime is alive.

---

## Duplicate Torrent Handling

AzuDl reads the torrent InfoHash before adding `.torrent` files. If the torrent is already registered in aria2, AzuDl will detect the existing torrent, show the existing GID, resume or monitor the existing task, and remove and re-add it if the existing task is errored.

---

## aria2 Status

Use:

```text
Torrent Tools > aria2 status
```

This shows:

```text
GID
Status
Name
InfoHash
Progress
Completed size
Download speed
Upload speed
Uploaded size
Ratio
Connections
Seeders
Errors
```

---

## Removing a Torrent Task

Use:

```text
Torrent Tools > Remove aria2 GID
```

Then paste the GID shown in aria2 status.

This can be useful when a torrent is stuck, duplicated, errored, or when you want to stop a seeding task.

---

## Batch Download

Batch download allows multiple links to be downloaded one by one.

Supported in batch mode:

- Direct links
- YouTube links
- Magnet links
- `.torrent` links

Unknown links are skipped.

---

## Download History

AzuDl stores download history in:

```text
/content/drive/MyDrive/AzuDl-GC2GD/Logs/download_history.json
```

History includes type, source, output, status, time, format, seed mode, and error message.

---

## File Management Tools

AzuDl includes:

```text
List downloaded files
Show latest file
Storage report
SHA256 latest file
SHA256 selected file
ZIP folder
ZIP latest folder
```

ZIP files are saved in:

```text
/content/drive/MyDrive/AzuDl-GC2GD/Archives
```

---

## Speed Limit Examples

```text
500K
2M
10M
```

Leave empty for no speed limit.

---

## Requirements

AzuDl installs required packages inside Colab:

```bash
apt install -y aria2 ffmpeg p7zip-full
pip install tqdm requests yt-dlp ipywidgets
```

| Tool | Purpose |
|---|---|
| aria2 | Direct, torrent, magnet downloads |
| ffmpeg | YouTube merging and audio extraction |
| yt-dlp | YouTube download engine |
| tqdm | Progress bars |
| requests | HTTP requests |
| ipywidgets | Colab GUI interface |
| p7zip-full | Archive support |

---

## How to Use

1. Open Google Colab: `https://colab.research.google.com`
2. Create a new notebook.
3. Paste the full AzuDl code into a cell.
4. Run the cell.
5. Authorize Google Drive mount.
6. Use the GUI or choose an option from the CLI menu.

---

## Recommended Usage

For public torrent files:

```text
Torrent Tools > Torrent file
```

For private tracker torrents:

```text
Torrent Tools > Private torrent
```

For YouTube:

```text
YouTube video or playlist
```

For direct files:

```text
Direct link
```

For mixed links:

```text
Auto detect link
```

---

## GitHub Safety

Never commit real credentials, cookies, tokens, session files, or private account data.

Recommended `.gitignore` entries:

```gitignore
cookies.txt
youtube_cookies.txt
youtube_po_token.txt
youtube_visitor_data.txt
github_token.txt
*_cookies.txt
*.cookies
*.token
aria2_rpc_secret.txt
aria2.session
download_history.json
```

---

## Legal Notice

Use AzuDl only for content that you have the right to download, store, or distribute. The developer is not responsible for misuse of this project. AzuDl is a downloader tool. Responsibility for the downloaded content belongs to the user.

---

## Limitations

- Google Colab can disconnect at any time.
- Colab is not suitable for permanent torrent seeding.
- Some direct links require authentication.
- Some websites block Colab IP addresses.
- Some YouTube videos may require cookies or may not be available in Colab.
- Private tracker seeding should be done on a VPS or seedbox for reliable long-term ratio.
- Google Drive write speed may vary.
- The GUI is currently beta and may receive layout or visual changes.

---

## Developer

```text
Developer: The Azizi
Project: AzuDl - GC2GD
Full Name: Azizi Universal Downloader - Google Colab to Google Drive
```

Links:

- X: https://x.com/the_azzi
- GitHub: https://github.com/TheGreatAzizi
- Telegram: https://t.me/luluch_code
- Git: https://git.theazizi.ir/TheAzizi
- Website: https://theazizi.ir

---

## Repository Description

```text
AzuDl - GC2GD is a Google Colab based universal downloader for downloading direct links, YouTube videos, playlists, magnet links, torrent files, and private torrents directly to Google Drive with a Colab GUI beta, aria2 resume support, live progress, seeding status, batch downloads, history, ZIP tools, and SHA256 utilities.
```

---

## Suggested Commit Message

```text
release: AzuDl GC2GD 1.4.20 GUI Beta
```

Alternative:

```text
feat(gui): add GitHub downloader diagnostics and verified Drive transfer
```

---

## Changelog

### 1.4.20 GUI Beta

- Added Colab widget-based GUI beta
- Added tab-based dashboard
- Added GUI tabs for Auto, Direct, YouTube, Torrent, Batch, Files, Archives, Maintenance, Developer, and Guide
- Added Google Drive storage cards and usage bar in the GUI
- Added GUI output console
- Added GUI buttons for common actions
- Added GUI access to cookie help and PO Token help
- Kept classic CLI available
- Set GUI as the default interface
- Improved public GitHub usability for new users

### v1.4.20 GUI Beta

- Added GitHub repository downloader
- Added Official project repository downloader
- Added GitHub token field, token status, and rate-limit display
- Added latest release, all releases, release tag, and default branch source download modes
- Added README and license download options for GitHub repositories
- Added verified Google Drive transfer workflow with chunked copy, fsync, sync, and visibility checks
- Added Force Drive sync tool
- Added Run diagnostic tool
- Improved GUI buttons, mobile tabs, Maintenance layout, and public user-facing text
- Fixed GitHub token recursion, GitHub info recursion, Official repo recursion, handler mismatches, and Diagnostic button visibility

### v1.2.8

- Added torrent InfoHash detection before adding `.torrent` files
- Added duplicate torrent detection
- Added resume/monitor behavior for existing aria2 torrent tasks
- Added automatic removal of existing errored torrent tasks
- Improved aria2 status output with InfoHash
- Kept dedicated Torrent Tools menu
- Kept private torrent mode
- Kept live seeding status
- Kept aria2 session persistence
- Kept YouTube audio format fix
- Kept ZIP, SHA256, history, and file tools

### v1.2.7

- Fixed tqdm bool error during seeding status display

### v1.2.6

- Moved torrent features into a dedicated Torrent Tools menu

### v1.2.5

- Added live torrent seeding status
- Added aria2 session persistence
- Added resume-friendly aria2 settings

### v1.2.4

- Fixed invalid infinite seed-time issue
- Replaced invalid `-1` seed time with long valid seed time

### v1.2.3

- Improved `.torrent` download validation
- Improved aria2 RPC error messages

---

## License
```text
MIT
```
