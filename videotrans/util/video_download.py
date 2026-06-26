import yt_dlp
from pathlib import Path
import uuid
import shutil
from typing import Callable, Optional
from videotrans.configure.config import TEMP_ROOT

class VideoDownloadError(RuntimeError):
    pass

def download_video(
    url: str,
    *,
    output_dir: Optional[str] = None,
    progress: Optional[Callable[[str], None]] = None,
) -> str:
    url = (url or "").strip()
    if not url.startswith("http"):
        raise VideoDownloadError("Vui lòng nhập link video hợp lệ (bắt đầu bằng http/https).")

    base_dir = Path(output_dir or (Path(TEMP_ROOT) / "quick_downloads"))
    target_dir = base_dir / f"job-{uuid.uuid4().hex[:10]}"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Cấu hình tải cơ bản nhất: lấy thẳng bản tốt nhất
    ydl_opts = {
        'format': 'best',
        'outtmpl': str(target_dir / '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True
    }

    if progress:
        def hook(d):
            if d.get('status') == 'downloading':
                progress(f"Đang tải video: {d.get('_percent_str', '0%')}")
            elif d.get('status') == 'finished':
                progress("Tải xong, đang chuẩn bị file...")
        ydl_opts['progress_hooks'] = [hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            
            # Đảm bảo đuôi file là mp4
            if not filepath.endswith('.mp4'):
                filepath = filepath.rsplit('.', 1)[0] + '.mp4'
                
            return filepath
    except Exception as e:
        shutil.rmtree(target_dir, ignore_errors=True)
        raise VideoDownloadError(f"Lỗi tải video: {str(e)}")