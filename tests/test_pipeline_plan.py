from pathlib import Path

from videotrans.pipeline.dag import transvideo_dag
from videotrans.pipeline.plan import (
    audio_normalize_plan,
    build_timeline,
    build_translation_batches,
    load_project_plan,
    save_project_plan,
    stable_key,
)


def test_stable_key_is_repeatable_for_download_cache():
    assert stable_key("https://example.com/video?id=1") == stable_key("https://example.com/video?id=1")
    assert stable_key("https://example.com/video?id=1") != stable_key("https://example.com/video?id=2")


def test_timeline_batches_and_plan_roundtrip(tmp_path: Path):
    subtitles = [
        {"line": 1, "start_time": 0, "end_time": 1000, "text": "mot"},
        {"line": 2, "start_time": 1200, "end_time": 2200, "text": "hai"},
        {"line": 3, "start_time": 2600, "end_time": 3200, "text": "ba"},
    ]
    timeline = build_timeline(subtitles, total_ms=4000)
    assert timeline[0]["slot_end_ms"] == 1200
    assert timeline[-1]["slot_end_ms"] == 4000

    batches = build_translation_batches(subtitles, max_lines=2)
    assert [batch["lines"] for batch in batches] == [[1, 2], [3]]

    plan = load_project_plan(tmp_path)
    plan.timeline = timeline
    plan.translation_batches = batches
    save_project_plan(tmp_path, plan)
    loaded = load_project_plan(tmp_path)
    assert loaded.timeline == timeline
    assert loaded.translation_batches == batches


def test_audio_nodes_are_skipped_without_dubbing():
    steps = transvideo_dag().plan(
        {
            "has_audio": True,
            "needs_recogn": True,
            "needs_translate": True,
            "needs_dubbing": False,
            "needs_subtitle": True,
        }
    )
    by_name = {step["name"]: step for step in steps}
    assert by_name["dubbing"]["status"] == "skipped"
    assert by_name["audio_normalize"]["status"] == "skipped"
    assert by_name["align"]["status"] == "skipped"
    assert by_name["render"]["enabled"] is True


def test_audio_normalize_plan_only_when_dubbing():
    assert audio_normalize_plan(enabled=False)["reason"] == "skip_no_dubbing"
    assert audio_normalize_plan(enabled=True, source_path="target.wav")["source_path"] == "target.wav"
