import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class GpuDiagnostic:
    ok: bool
    summary: str
    details: tuple[str, ...]


def _run(args: list[str], timeout: int = 8) -> tuple[int, str]:
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout, errors="replace")
        return proc.returncode, (proc.stdout or proc.stderr or "").strip()
    except Exception as e:
        return 1, str(e)


def diagnose_gpu() -> GpuDiagnostic:
    details: list[str] = []
    ok = False

    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi:
        code, out = _run([nvidia_smi, "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"])
        if code == 0 and out:
            ok = True
            details.append(f"NVIDIA: {out.splitlines()[0]}")
        else:
            details.append(f"NVIDIA check failed: {out}")
    else:
        details.append("Không tìm thấy nvidia-smi.")

    try:
        import torch

        if torch.cuda.is_available():
            ok = True
            details.append(f"Torch CUDA: {torch.version.cuda}; device={torch.cuda.get_device_name(0)}")
        else:
            details.append("Torch CUDA không khả dụng, sẽ fallback CPU.")
    except Exception as e:
        details.append(f"Torch CUDA check skipped: {e}")

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        code, out = _run([ffmpeg, "-hide_banner", "-encoders"], timeout=10)
        if code == 0:
            encoders = []
            for name in ["h264_nvenc", "hevc_nvenc", "h264_qsv", "h264_amf"]:
                if name in out:
                    encoders.append(name)
            details.append("FFmpeg GPU encoders: " + (", ".join(encoders) if encoders else "không thấy encoder phần cứng"))
    else:
        details.append("Không tìm thấy ffmpeg trong PATH.")

    summary = "GPU sẵn sàng" if ok else "GPU chưa sẵn sàng, dùng CPU"
    return GpuDiagnostic(ok=ok, summary=summary, details=tuple(details))
