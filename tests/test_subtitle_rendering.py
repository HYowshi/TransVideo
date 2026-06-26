from videotrans.util.help_srt import (
    DEFAULT_ASS_STYLE,
    _load_ass_style,
    simple_wrap,
    subtitle_display_width,
)


def test_subtitle_display_width_weights_cjk_more_than_latin():
    assert subtitle_display_width("你好") > subtitle_display_width("ab")


def test_simple_wrap_prefers_vietnamese_word_boundaries():
    wrapped = simple_wrap(
        "Đây là một câu tiếng Việt khá dài cần được ngắt tự nhiên",
        maxlen=18,
        language="vi",
    )

    assert "\n" in wrapped
    assert "Việ\nt" not in wrapped


def test_simple_wrap_handles_cjk_without_spaces():
    wrapped = simple_wrap("这是一个需要自然断行的中文字幕测试", maxlen=8, language="zh-cn")

    assert "\n" in wrapped
    assert all(line.strip() for line in wrapped.splitlines())


def test_default_ass_style_covers_original_subtitles():
    assert DEFAULT_ASS_STYLE["BorderStyle"] == 3
    assert DEFAULT_ASS_STYLE["BackColour"] != "&H00000000&"
    assert DEFAULT_ASS_STYLE["MarginV"] >= 20


def test_load_ass_style_returns_builtin_cover_style_without_ass_json(monkeypatch):
    monkeypatch.setattr("videotrans.util.help_srt.os.path.exists", lambda _: False)
    monkeypatch.setattr(
        "videotrans.util.help_srt.settings",
        {"subtitle_cover_original": True},
    )

    style = _load_ass_style()

    assert style["BorderStyle"] == 3
    assert style["BackColour"] == DEFAULT_ASS_STYLE["BackColour"]
