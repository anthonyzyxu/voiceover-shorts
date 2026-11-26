import pytest
from pydantic import ValidationError
from schema import parse_transcript, parse_slides

VALID_TRANSCRIPT = {
    "audio_file": "audio/input.wav",
    "language": "zh",
    "model": "large-v3",
    "segments": [
        {
            "id": 0,
            "start": 0.0,
            "end": 3.2,
            "text": "今天跟大家聊。",
            "words": [{"word": "今天", "start": 0.0, "end": 0.5}],
        }
    ],
}


def _slides(slides):
    return {"title": "主題", "duration": 179.0, "slides": slides}


def _bullet(text="第一條重點", start=0.0, end=5.0):
    return {"text": text, "start": start, "end": end, "highlight": []}


def _slide(index=0, start=0.0, end=10.0, title="主標題", bullets=None):
    if bullets is None:
        bullets = [_bullet(), _bullet("第二條重點", 5.0, 10.0)]
    return {
        "index": index,
        "start": start,
        "end": end,
        "chapterLabel": "開場",
        "title": title,
        "bullets": bullets,
    }


def _three_slides():
    return [_slide(0, 0.0, 10.0), _slide(1, 10.0, 20.0), _slide(2, 20.0, 30.0)]


def test_parse_transcript_ok():
    t = parse_transcript(VALID_TRANSCRIPT)
    assert t.segments[0].text == "今天跟大家聊。"
    assert t.segments[0].words[0].end == 0.5


def test_parse_slides_ok():
    s = parse_slides(_slides(_three_slides()))
    assert len(s.slides) == 3
    assert s.slides[0].title == "主標題"


def test_title_over_10_chars_rejected():
    data = _slides(
        [_slide(title="這是一個超過十個字的超長主標題"), _slide(1, 10.0, 20.0), _slide(2, 20.0, 30.0)]
    )
    with pytest.raises(ValidationError):
        parse_slides(data)


def test_bullet_over_15_chars_rejected():
    bullets = [
        _bullet("這是一條超過十五個字的超長重點列表項目"),
        _bullet("第二條", 5.0, 10.0),
    ]
    data = _slides([_slide(bullets=bullets), _slide(1, 10.0, 20.0), _slide(2, 20.0, 30.0)])
    with pytest.raises(ValidationError):
        parse_slides(data)


def test_bullet_count_out_of_range_rejected():
    data = _slides(
        [_slide(bullets=[_bullet()]), _slide(1, 10.0, 20.0), _slide(2, 20.0, 30.0)]
    )
    with pytest.raises(ValidationError):
        parse_slides(data)


def test_slide_count_out_of_range_rejected():
    data = _slides([_slide(0, 0.0, 10.0), _slide(1, 10.0, 20.0)])
    with pytest.raises(ValidationError):
        parse_slides(data)


def test_start_after_end_rejected():
    data = _slides([_slide(start=10.0, end=5.0), _slide(1, 10.0, 20.0), _slide(2, 20.0, 30.0)])
    with pytest.raises(ValidationError):
        parse_slides(data)
