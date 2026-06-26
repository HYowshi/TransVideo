import importlib.util
import re
from pathlib import Path
from typing import Callable, Optional

from videotrans.configure.config import TEMP_ROOT


class VideoDownloadError(RuntimeError):
    pass


def is_video_url(value: str) -> bool:
    value = (value or "").strip()
    return bool(re.match(r"^https?://\S+$", value, flags=re.I))


def _require_ytdlp():
    if importlib.util.find_spec("yt_dlp") is None:
        raise VideoDownloadError(
            "Missing dependency: yt-dlp. Install it with: uv add yt-dlp"
        )
    from yt_dlp import YoutubeDL

    return YoutubeDL


def download_video(
    url: str,
    *,
    output_dir: Optional[str] = None,
    progress: Optional[Callable[[str], None]] = None,
) -> str:
    url = (url or "").strip()
    if not is_video_url(url):
        raise VideoDownloadError("Please enter a valid http/https video URL.")

    YoutubeDL = _require_ytdlp()
    target_dir = Path(output_dir or (Path(TEMP_ROOT) / "quick_downloads"))
    target_dir.mkdir(parents=True, exist_ok=True)

    def hook(d):
        if not progress:
            return
        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("_percent_str", "").strip()
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            parts = [p for p in [downloaded, speed, f"ETA {eta}" if eta else ""] if p]
            progress("Downloading video " + " | ".join(parts))
        elif status == "finished":
            progress("Download finished, preparing video file...")

    options = {
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",
        "outtmpl": str(target_dir / "%(title).180B-%(id)s.%(ext)s"),
        "noplaylist": True,
        "restrictfilenames": True,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [hook],
    }

    try:
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_path = ydl.prepare_filename(info)
            requested = info.get("requested_downloads") or []
            if requested and requested[0].get("filepath"):
                downloaded_path = requested[0]["filepath"]
    except Exception as e:
        raise VideoDownloadError(str(e)) from e

    path = Path(downloaded_path)
    if path.suffix.lower() != ".mp4":
        mp4_path = path.with_suffix(".mp4")
        if mp4_path.exists():
            path = mp4_path

    if not path.exists():
        matches = sorted(target_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if matches:
            path = matches[0]

    if not path.exists():
        raise VideoDownloadError("Video download completed but output file was not found.")

    return path.resolve().as_posix()
