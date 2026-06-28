import importlib.util
import re
import shutil
import uuid
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse

from videotrans.configure.config import TEMP_ROOT


class VideoDownloadError(RuntimeError):
    pass


def is_video_url(value: str) -> bool:
    value = (value or "").strip()
    return bool(re.match(r"^https?://\S+$", value, flags=re.I))


def _require_ytdlp():
    if importlib.util.find_spec("yt_dlp") is None:
        raise VideoDownloadError("Thiếu yt-dlp. Hãy chạy lại phần tải runtime của TransVideo.")
    from yt_dlp import YoutubeDL

    return YoutubeDL


def _host(url: str) -> str:
    return urlparse(url).netloc.lower()


def _is_bilibili_url(url: str) -> bool:
    host = _host(url)
    return "bilibili.com" in host or "b23.tv" in host


def _friendly_download_error(url: str, message: str) -> str:
    raw = message or ""
    lowered = raw.lower()
    if _is_bilibili_url(url) and ("http error 412" in lowered or "precondition failed" in lowered):
        return (
            "Không tải được video BiliBili vì máy chủ trả HTTP 412 Precondition Failed.\n\n"
            "Hãy mở link bằng Edge/Chrome, đăng nhập nếu cần, phát thử vài giây, rồi quay lại TransVideo bấm Start lại. "
            "Nếu vẫn lỗi, website đang chặn tải tự động và bạn nên tải MP4 thủ công rồi chọn file trong app."
        )
    if "unsupported url" in lowered:
        return "Link này chưa được yt-dlp hỗ trợ. Hãy thử link khác hoặc tải video thủ công rồi chọn file MP4."
    if "private video" in lowered or "login" in lowered:
        return "Video cần đăng nhập hoặc không công khai. Hãy mở trong trình duyệt, đăng nhập, rồi thử lại."
    return raw


def _browser_cookie_attempts(url: str) -> list[tuple[str, ...]]:
    if _is_bilibili_url(url):
        return [("edge",), ("chrome",), ("firefox",)]
    host = _host(url)
    if any(name in host for name in ["youtube.com", "youtu.be", "tiktok.com", "facebook.com"]):
        return [("edge",), ("chrome",)]
    return []


def _format_attempts() -> list[tuple[str, str]]:
    return [
        ("siêu chất lượng", "bv*[height<=2160]+ba/b[height<=2160]/bv*+ba/best"),
        ("MP4 chất lượng cao", "bestvideo[ext=mp4][height<=2160]+bestaudio[ext=m4a]/best[ext=mp4]/best"),
        ("1080p ổn định", "bv*[height<=1080]+ba/b[height<=1080]/best[height<=1080]/best"),
        ("file đơn tương thích", "best"),
    ]


def download_video(
    url: str,
    *,
    output_dir: Optional[str] = None,
    progress: Optional[Callable[[str], None]] = None,
) -> str:
    url = (url or "").strip()
    if not is_video_url(url):
        raise VideoDownloadError("Hãy nhập link video hợp lệ, bắt đầu bằng http:// hoặc https://.")

    YoutubeDL = _require_ytdlp()
    base_dir = Path(output_dir or (Path(TEMP_ROOT) / "quick_downloads"))
    target_dir = base_dir / f"job-{uuid.uuid4().hex[:10]}"
    target_dir.mkdir(parents=True, exist_ok=True)

    def hook(d):
        if not progress:
            return
        status = d.get("status")
        if status == "downloading":
            percent = d.get("_percent_str", "").strip()
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            parts = [p for p in [percent, speed, f"ETA {eta}" if eta else ""] if p]
            progress("Đang tải video " + " | ".join(parts))
        elif status == "finished":
            progress("Tải xong, đang ghép/chuẩn hóa file...")

    base_options = {
        "merge_output_format": "mp4",
        "outtmpl": str(target_dir / "%(title).180B-%(id)s.%(ext)s"),
        "paths": {"home": str(target_dir)},
        "noplaylist": True,
        "ignoreerrors": False,
        "restrictfilenames": True,
        "windowsfilenames": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 8,
        "fragment_retries": 8,
        "file_access_retries": 5,
        "extractor_retries": 5,
        "socket_timeout": 60,
        "continuedl": True,
        "nopart": False,
        "concurrent_fragment_downloads": 8,
        "http_chunk_size": 10 * 1024 * 1024,
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ),
        "progress_hooks": [hook],
    }
    if _is_bilibili_url(url):
        base_options["referer"] = "https://www.bilibili.com/"
        base_options["extractor_args"] = {"bilibili": {"prefer_multi_flv": ["False"]}}

    def extract(attempt_options):
        with YoutubeDL(attempt_options) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            requested = info.get("requested_downloads") or []
            if requested and requested[0].get("filepath"):
                path = requested[0]["filepath"]
            return path

    try:
        last_error = None
        downloaded_path = None
        for browser in [None] + _browser_cookie_attempts(url):
            for label, fmt in _format_attempts():
                opts = dict(base_options)
                opts["format"] = fmt
                if browser:
                    opts["cookiesfrombrowser"] = browser
                if progress:
                    suffix = f" bằng cookie {browser[0].title()}" if browser else ""
                    progress(f"Đang thử tải {label}{suffix}...")
                try:
                    downloaded_path = extract(opts)
                    break
                except Exception as e:
                    last_error = e
            if downloaded_path:
                break
        if not downloaded_path:
            raise last_error or VideoDownloadError("Không tải được video.")
    except Exception as e:
        shutil.rmtree(target_dir, ignore_errors=True)
        raise VideoDownloadError(_friendly_download_error(url, str(e))) from e

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
        shutil.rmtree(target_dir, ignore_errors=True)
        raise VideoDownloadError("Tải video xong nhưng không tìm thấy file đầu ra.")

    return path.resolve().as_posix()
