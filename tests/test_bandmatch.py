from videotrans.bandmatch import analyze_subtitles, estimate_speech_ms, line_pressure_map, recommend_tuning
from videotrans.task.taskcfg import SrtItem


def _sub(text, start, end, line=1):
    return SrtItem(text=text, start_time=start, end_time=end, line=line)


def test_estimate_speech_ms_increases_with_text_load():
    short = estimate_speech_ms("xin chào", language="vi")
    long = estimate_speech_ms("xin chào các bạn hôm nay chúng ta sẽ xem một video rất thú vị", language="vi")

    assert long > short


def test_analyze_subtitles_flags_dense_lines():
    report = analyze_subtitles(
        [
            _sub("câu rất ngắn", 0, 2500, 1),
            _sub("đây là một câu tiếng Việt rất dài cần đọc trong một khoảng thời gian cực ngắn", 2500, 3500, 2),
        ],
        language="vi",
    )

    assert report.score < 100
    assert report.risky_ratio > 0
    assert report.lines[1].risk in {"medium", "high"}
    assert report.suggested_total_ms >= report.original_total_ms


def test_recommend_tuning_enables_autorate_for_dense_subtitles():
    report = analyze_subtitles(
        [_sub("nội dung rất dài cần được đọc nhanh hơn nhiều so với timeline gốc", 0, 900, 1)],
        language="vi",
    )
    tuning = recommend_tuning(report)

    assert tuning.voice_autorate is True
    assert tuning.voice_rate_percent > 0


def test_recommend_tuning_keeps_stable_timeline_for_easy_subtitles():
    report = analyze_subtitles([_sub("xin chào", 0, 3000, 1)], language="vi")
    tuning = recommend_tuning(report)

    assert tuning.voice_autorate is False
    assert tuning.video_autorate is False
    assert tuning.align_sub_audio is True


def test_line_pressure_map_indexes_by_subtitle_line():
    report = analyze_subtitles([_sub("xin chào", 1200, 2200, 7)], language="vi")
    mapped = line_pressure_map(report)

    assert 7 in mapped
    assert mapped[7].suggested_slot_ms >= mapped[7].slot_ms
