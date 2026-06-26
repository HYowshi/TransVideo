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


def _is_bilibili_url(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return "bilibili.com" in host or "b23.tv" in host


def _friendly_download_error(url: str, message: str) -> str:
    raw = message or ""
    lowered = raw.lower()
    if _is_bilibili_url(url) and ("http error 412" in lowered or "precondition failed" in lowered):
        return (
            "Không tải được video BiliBili vì máy chủ trả HTTP 412 Precondition Failed.\n\n"
            "Nguyên nhân thường gặp: video cần đăng nhập/cookie, bị giới hạn vùng, link BiliBili chặn tải tự động, "
            "hoặc trình duyệt chưa từng mở video đó.\n\n"
            "Cách xử lý: mở link bằng Edge hoặc Chrome trên máy này, đăng nhập BiliBili nếu cần, phát thử video vài giây, "
            "rồi quay lại TransVideo bấm Start lại. Nếu vẫn lỗi, hãy tải video thủ công rồi chọn file MP4 trong app."
        )
    if "unsupported url" in lowered:
        return "Link này chưa được yt-dlp hỗ trợ. Hãy thử link khác hoặc tải video thủ công rồi chọn file MP4."
    if "private video" in lowered or "login" in lowered:
        return "Video này có vẻ cần đăng nhập hoặc không công khai. Hãy mở video trong trình duyệt, đăng nhập, rồi thử lại."
    return raw


def _require_ytdlp():
    if importlib.util.find_spec("yt_dlp") is None:
        raise VideoDownloadError(
            "Thiếu thư viện yt-dlp. Hãy chạy lại phần tải runtime của TransVideo."
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
            downloaded = d.get("_percent_str", "").strip()
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            parts = [p for p in [downloaded, speed, f"ETA {eta}" if eta else ""] if p]
            progress("Đang tải video " + " | ".join(parts))
        elif status == "finished":
            progress("Tải xong, đang chuẩn bị file video...")

    options = {
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",
        "outtmpl": str(target_dir / "%(title).180B-%(id)s.%(ext)s"),
        "noplaylist": True,
        "restrictfilenames": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 3,
        "fragment_retries": 3,
        "socket_timeout": 30,
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ),
        "progress_hooks": [hook],
    }
    if _is_bilibili_url(url):
        options["referer"] = "https://www.bilibili.com/"

    try:
        try:
            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
        except Exception as first_error:
            if not _is_bilibili_url(url):
                raise
            last_error = first_error
            for browser in ("edge", "chrome"):
                retry_options = dict(options)
                retry_options["cookiesfrombrowser"] = (browser,)
                if progress:
                    progress(f"BiliBili bị chặn, đang thử cookie từ {browser.title()}...")
                try:
                    with YoutubeDL(retry_options) as ydl:
                        info = ydl.extract_info(url, download=True)
                    break
                except Exception as cookie_error:
                    last_error = cookie_error
            else:
                raise last_error
        downloaded_path = ydl.prepare_filename(info)
        requested = info.get("requested_downloads") or []
        if requested and requested[0].get("filepath"):
            downloaded_path = requested[0]["filepath"]
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
