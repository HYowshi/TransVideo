from videotrans.task.taskcfg import SrtItem
from videotrans.util.help_srt import ms_to_time_string
from videotrans.translator.guard import align_srt_result, preserve_missing_lines, split_text_result


def _item(text, line=1, start=0, end=1000):
    startraw = ms_to_time_string(ms=start)
    endraw = ms_to_time_string(ms=end)
    return SrtItem(
        line=line,
        start_time=start,
        end_time=end,
        startraw=startraw,
        endraw=endraw,
        time=f"{startraw} --> {endraw}",
        text=text,
    )


def test_split_text_result_removes_numbered_prefixes():
    result = split_text_result("1. Xin chào\n2) Tạm biệt", 2)

    assert result == ["Xin chào", "Tạm biệt"]


def test_preserve_missing_lines_falls_back_to_source_text():
    source = [_item("gốc 1"), _item("gốc 2", line=2)]

    assert preserve_missing_lines(source, ["dịch 1"]) == ["dịch 1", "gốc 2"]


def test_align_srt_result_keeps_source_timeline_when_ai_drops_line():
    source = [_item("a", 1, 0, 1000), _item("b", 2, 1000, 2000)]
    translated = [_item("xin chào", 1, 0, 1000)]

    aligned = align_srt_result(source, translated)

    assert len(aligned) == 2
    assert aligned[0].text == "xin chào"
    assert aligned[1].text == "b"
    assert aligned[1].start_time == 1000
