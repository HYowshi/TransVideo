from videotrans.configure.config import settings


def preferred_audio_encode_args(*, normalize: bool = True, bitrate: str = "192k") -> list[str]:
    args: list[str] = []
    if normalize:
        args.extend(["-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000"])
    args.extend(["-ac", "2", "-ar", "48000", "-b:a", bitrate, "-c:a", "aac"])
    return args


def preferred_video_encode_args() -> list[str]:
    try:
        configured = int(settings.get("crf", 23))
    except (TypeError, ValueError):
        configured = 23
    crf = min(configured, 18)
    preset = str(settings.get("preset", "medium") or "medium")
    if preset in {"ultrafast", "superfast", "veryfast"}:
        preset = "medium"
    return ["-crf", str(crf), "-preset", preset, "-pix_fmt", "yuv420p"]


def preferred_movflags() -> list[str]:
    return ["-movflags", "+faststart", "-max_muxing_queue_size", "4096"]
