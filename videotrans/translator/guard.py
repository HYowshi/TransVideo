import re
from typing import Iterable, List

from videotrans.task.taskcfg import SrtItem


_LINE_PREFIX_RE = re.compile(r"^\s*(?:\d+[\).\]\-:]\s*|[-*]\s+)")


def clean_translated_line(text: str) -> str:
    text = (text or "").strip()
    text = _LINE_PREFIX_RE.sub("", text).strip()
    return re.sub(r"\s+", " ", text)


def split_text_result(result: str, expected_count: int) -> list[str]:
    lines = [clean_translated_line(line) for line in (result or "").splitlines()]
    lines = [line for line in lines if line]
    if len(lines) == expected_count:
        return lines
    if expected_count == 1:
        return [clean_translated_line(result)]
    if len(lines) > expected_count:
        head = lines[: expected_count - 1]
        tail = " ".join(lines[expected_count - 1 :])
        return head + [tail]
    return lines


def preserve_missing_lines(source_items: Iterable[SrtItem], translated_lines: list[str]) -> list[str]:
    source = list(source_items)
    output: list[str] = []
    for idx, item in enumerate(source):
        translated = translated_lines[idx].strip() if idx < len(translated_lines) else ""
        output.append(translated or item["text"])
    return output


def align_srt_result(source_items: List[SrtItem], translated_items: List[SrtItem]) -> List[SrtItem]:
    if len(source_items) == len(translated_items):
        aligned = translated_items
    else:
        by_time = {item.get("time", ""): item for item in translated_items if item.get("time")}
        aligned = []
        for idx, src in enumerate(source_items):
            candidate = by_time.get(src.get("time", "")) or (translated_items[idx] if idx < len(translated_items) else None)
            text = candidate["text"].strip() if candidate and candidate.get("text") else src["text"]
            aligned.append(
                SrtItem(
                    line=src["line"],
                    start_time=src["start_time"],
                    end_time=src["end_time"],
                    startraw=src["startraw"],
                    endraw=src["endraw"],
                    time=src["time"],
                    text=text,
                    spk=src.get("spk", ""),
                    filename=src.get("filename", ""),
                )
            )
        return aligned

    for idx, item in enumerate(aligned):
        if not item["text"].strip() and idx < len(source_items):
            item["text"] = source_items[idx]["text"]
    return aligned
