import re
from dataclasses import dataclass
from statistics import mean
from typing import Iterable, Sequence


_CJK_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
_WORD_RE = re.compile(r"[A-Za-zÀ-ỹ0-9]+", re.UNICODE)


@dataclass(frozen=True)
class BandMatchLine:
    line: int
    start_time: int
    end_time: int
    slot_ms: int
    gap_before_ms: int
    text_units: float
    estimated_speech_ms: int
    pressure: float
    risk: str


@dataclass(frozen=True)
class BandMatchReport:
    lines: tuple[BandMatchLine, ...]
    score: int
    avg_pressure: float
    p90_pressure: float
    risky_ratio: float
    overlap_count: int
    long_gap_ratio: float


@dataclass(frozen=True)
class BandMatchTuning:
    voice_autorate: bool
    video_autorate: bool
    remove_silent_mid: bool
    align_sub_audio: bool
    voice_rate_percent: int
    reason: str


def _as_int(value, default: int = 0) -> int:
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return default


def text_units(text: str) -> float:
    """Estimate speaking load across CJK and Latin/Vietnamese text."""
    text = (text or "").strip()
    if not text:
        return 0.0
    cjk_count = len(_CJK_RE.findall(text))
    words = _WORD_RE.findall(_CJK_RE.sub(" ", text))
    latin_units = sum(max(1.0, len(word) / 4.2) for word in words)
    punctuation_pause_units = len(re.findall(r"[,.!?;:，。！？；：]", text)) * 0.45
    return cjk_count * 1.0 + latin_units + punctuation_pause_units


def estimate_speech_ms(text: str, language: str = "vi") -> int:
    """Return a conservative TTS duration estimate in milliseconds."""
    units = text_units(text)
    if units <= 0:
        return 0
    lang = (language or "").lower()
    if lang.startswith(("zh", "ja", "ko", "yue")):
        units_per_second = 5.2
    elif lang.startswith("vi"):
        units_per_second = 3.55
    else:
        units_per_second = 3.85
    estimated = int(round((units / units_per_second) * 1000))
    return max(550, estimated)


def _percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * percentile))))
    return ordered[idx]


def _risk_for_pressure(pressure: float) -> str:
    if pressure >= 1.35:
        return "high"
    if pressure >= 1.08:
        return "medium"
    return "low"


def analyze_subtitles(subtitles: Iterable, *, language: str = "vi") -> BandMatchReport:
    rows: list[BandMatchLine] = []
    previous_end = 0
    overlaps = 0
    long_gaps = 0

    for index, item in enumerate(subtitles, start=1):
        getter = item.get if hasattr(item, "get") else lambda key, default=None: getattr(item, key, default)
        start = _as_int(getter("start_time", 0))
        end = _as_int(getter("end_time", start))
        text = str(getter("text", "") or "")
        slot_ms = max(1, end - start)
        gap_before = start - previous_end
        if gap_before < 0:
            overlaps += 1
        if gap_before > 1200:
            long_gaps += 1
        estimated = estimate_speech_ms(text, language=language)
        pressure = estimated / slot_ms if estimated else 0.0
        rows.append(
            BandMatchLine(
                line=_as_int(getter("line", index), index),
                start_time=start,
                end_time=end,
                slot_ms=slot_ms,
                gap_before_ms=gap_before,
                text_units=round(text_units(text), 2),
                estimated_speech_ms=estimated,
                pressure=round(pressure, 3),
                risk=_risk_for_pressure(pressure),
            )
        )
        previous_end = max(previous_end, end)

    pressures = [line.pressure for line in rows if line.estimated_speech_ms > 0]
    risky = [line for line in rows if line.risk in {"medium", "high"}]
    avg_pressure = mean(pressures) if pressures else 0.0
    p90_pressure = _percentile(pressures, 0.9)
    risky_ratio = len(risky) / len(rows) if rows else 0.0
    long_gap_ratio = long_gaps / len(rows) if rows else 0.0
    pressure_penalty = max(0.0, p90_pressure - 1.0) * 55
    risk_penalty = risky_ratio * 30
    overlap_penalty = min(25, overlaps * 5)
    score = int(round(max(0, min(100, 100 - pressure_penalty - risk_penalty - overlap_penalty))))
    return BandMatchReport(
        lines=tuple(rows),
        score=score,
        avg_pressure=round(avg_pressure, 3),
        p90_pressure=round(p90_pressure, 3),
        risky_ratio=round(risky_ratio, 3),
        overlap_count=overlaps,
        long_gap_ratio=round(long_gap_ratio, 3),
    )


def recommend_tuning(report: BandMatchReport) -> BandMatchTuning:
    pressure = report.p90_pressure
    needs_audio_rate = pressure >= 1.05 or report.risky_ratio >= 0.15
    needs_video_rate = pressure >= 1.35 or report.risky_ratio >= 0.35
    voice_rate = 0
    if pressure >= 1.08:
        voice_rate = min(18, max(4, int(round((pressure - 1.0) * 28))))
    if needs_video_rate:
        reason = "Nhiều câu dịch dài hơn thời lượng gốc, nên bật cả tăng tốc giọng và nới timeline video."
    elif needs_audio_rate:
        reason = "Một số câu có nguy cơ đọc dài hơn slot, nên bật tăng tốc giọng tự động."
    else:
        reason = "Nhịp phụ đề khá ổn, ưu tiên giữ timeline gốc và chỉ căn audio/sub."
    return BandMatchTuning(
        voice_autorate=needs_audio_rate,
        video_autorate=needs_video_rate,
        remove_silent_mid=(not needs_audio_rate and not needs_video_rate and report.long_gap_ratio >= 0.18),
        align_sub_audio=True,
        voice_rate_percent=voice_rate,
        reason=reason,
    )


def apply_tuning_to_main_window(main, tuning: BandMatchTuning) -> None:
    main.voice_autorate.setChecked(tuning.voice_autorate)
    main.video_autorate.setChecked(tuning.video_autorate)
    main.remove_silent_mid.setChecked(tuning.remove_silent_mid)
    main.align_sub_audio.setChecked(tuning.align_sub_audio)
    if hasattr(main, "voice_rate"):
        main.voice_rate.setValue(tuning.voice_rate_percent)
