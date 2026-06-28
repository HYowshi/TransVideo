import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

from videotrans.configure.config import logger
from videotrans.util.help_srt import get_subtitle_from_srt


PLAN_VERSION = 1


@dataclass
class ProjectPlan:
    version: int = PLAN_VERSION
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    source_url: str = ""
    source_path: str = ""
    cache_key: str = ""
    video: dict[str, Any] = field(default_factory=dict)
    audio: dict[str, Any] = field(default_factory=dict)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    translation_batches: list[dict[str, Any]] = field(default_factory=list)
    bandmatch: dict[str, Any] = field(default_factory=dict)
    subtitles: dict[str, Any] = field(default_factory=dict)
    audio_normalize: dict[str, Any] = field(default_factory=dict)
    render: dict[str, Any] = field(default_factory=dict)
    dag: dict[str, Any] = field(default_factory=lambda: {"nodes": {}, "completed": []})


def stable_key(value: str) -> str:
    return hashlib.sha256((value or "").strip().encode("utf-8", errors="ignore")).hexdigest()[:16]


def plan_path(folder: str | Path) -> Path:
    return Path(folder) / "project_plan.json"


def load_project_plan(folder: str | Path) -> ProjectPlan:
    path = plan_path(folder)
    if not path.exists():
        return ProjectPlan()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return ProjectPlan(**{k: v for k, v in data.items() if k in ProjectPlan.__dataclass_fields__})
    except Exception as e:
        logger.warning(f"[ProjectPlan] Cannot read {path}: {e}")
        return ProjectPlan()


def save_project_plan(folder: str | Path, plan: ProjectPlan) -> Path:
    path = plan_path(folder)
    path.parent.mkdir(parents=True, exist_ok=True)
    plan.updated_at = time.time()
    path.write_text(json.dumps(asdict(plan), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def update_project_plan(folder: str | Path, updater: Callable[[ProjectPlan], None]) -> ProjectPlan:
    plan = load_project_plan(folder)
    updater(plan)
    save_project_plan(folder, plan)
    return plan


def mark_node(plan: ProjectPlan, name: str, *, status: str = "done", **meta: Any) -> None:
    plan.dag.setdefault("nodes", {})[name] = {"status": status, "updated_at": time.time(), **meta}
    completed = plan.dag.setdefault("completed", [])
    if status == "done" and name not in completed:
        completed.append(name)


def split_video_audio_info(video_info: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    video = {
        "duration_ms": int(video_info.get("time") or 0),
        "fps": video_info.get("video_fps"),
        "codec": video_info.get("video_codec_name"),
        "width": video_info.get("width"),
        "height": video_info.get("height"),
        "color": video_info.get("color"),
        "streams": int(video_info.get("video_streams") or 0),
    }
    audio = {
        "codec": video_info.get("audio_codec_name"),
        "streams": int(video_info.get("streams_audio") or 0),
        "normalize_target": None,
    }
    return video, audio


def build_timeline(subtitles: Iterable[dict[str, Any]], *, total_ms: int = 0) -> list[dict[str, Any]]:
    items = list(subtitles or [])
    timeline = []
    for idx, item in enumerate(items):
        start = int(item.get("start_time") or 0)
        end = int(item.get("end_time") or start)
        next_start = int(items[idx + 1].get("start_time") or end) if idx + 1 < len(items) else int(total_ms or end)
        slot_end = max(end, next_start if next_start > start else end)
        timeline.append(
            {
                "line": int(item.get("line") or idx + 1),
                "start_ms": start,
                "end_ms": end,
                "slot_start_ms": start,
                "slot_end_ms": slot_end,
                "duration_ms": max(0, end - start),
                "slot_duration_ms": max(0, slot_end - start),
                "source_text": item.get("text", ""),
                "target_text": "",
                "has_speech": bool(str(item.get("text", "")).strip()),
            }
        )
    return timeline


def build_translation_batches(
    subtitles: Iterable[dict[str, Any]], *, max_lines: int = 4, max_chars: int = 650
) -> list[dict[str, Any]]:
    batches = []
    current = []
    current_chars = 0
    for item in subtitles or []:
        text = str(item.get("text", "")).strip()
        item_chars = len(text)
        if current and (len(current) >= max_lines or current_chars + item_chars > max_chars):
            batches.append(_batch_payload(current))
            current = []
            current_chars = 0
        current.append(item)
        current_chars += item_chars
    if current:
        batches.append(_batch_payload(current))
    return batches


def _batch_payload(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "lines": [int(it.get("line") or 0) for it in items],
        "start_ms": int(items[0].get("start_time") or 0),
        "end_ms": int(items[-1].get("end_time") or 0),
        "text": "\n".join(str(it.get("text", "")).strip() for it in items),
    }


def audio_normalize_plan(*, enabled: bool, source_path: str = "", target_lufs: int = -16) -> dict[str, Any]:
    if not enabled:
        return {"enabled": False, "reason": "skip_no_dubbing"}
    return {
        "enabled": True,
        "source_path": source_path,
        "target_lufs": target_lufs,
        "true_peak": -1.5,
        "lra": 11,
        "sample_rate": 48000,
        "channels": 2,
    }


def update_timeline_target_text(folder: str | Path, target_sub: str) -> None:
    if not Path(target_sub).exists():
        return
    target_items = {int(it.get("line") or 0): it.get("text", "") for it in get_subtitle_from_srt(target_sub)}

    def updater(plan: ProjectPlan) -> None:
        for segment in plan.timeline:
            segment["target_text"] = target_items.get(int(segment.get("line") or 0), "")
        plan.subtitles["target_srt"] = target_sub
        mark_node(plan, "translate", target_sub=target_sub)

    update_project_plan(folder, updater)

