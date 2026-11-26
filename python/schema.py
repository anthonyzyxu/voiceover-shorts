"""transcript.json 與 slides.json 的資料契約驗證（pydantic v2）。

第二步（Claude 文案策劃）與 Remotion 端都依賴這兩份 JSON 的欄位結構；
本模組是唯一事實來源，字數與數量上限來自規格。
"""

from typing import List

from pydantic import BaseModel, Field, model_validator


def _check_start_end(self):
    if self.start > self.end:
        raise ValueError("start 必須 <= end")
    return self


class Word(BaseModel):
    word: str
    start: float
    end: float

    _check = model_validator(mode="after")(_check_start_end)


class Segment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    words: List[Word]

    _check = model_validator(mode="after")(_check_start_end)


class Transcript(BaseModel):
    audio_file: str
    language: str
    model: str
    segments: List[Segment]


class Highlight(BaseModel):
    word: str
    start: float
    end: float

    _check = model_validator(mode="after")(_check_start_end)


class Bullet(BaseModel):
    text: str = Field(min_length=1, max_length=15)
    start: float
    end: float
    highlight: List[Highlight] = Field(default_factory=list)

    _check = model_validator(mode="after")(_check_start_end)


class Slide(BaseModel):
    index: int
    start: float
    end: float
    chapterLabel: str
    title: str = Field(min_length=1, max_length=10)
    bullets: List[Bullet] = Field(min_length=2, max_length=4)

    _check = model_validator(mode="after")(_check_start_end)


class Slides(BaseModel):
    title: str
    duration: float
    slides: List[Slide] = Field(min_length=3, max_length=6)


def parse_transcript(data: dict) -> Transcript:
    return Transcript.model_validate(data)


def parse_slides(data: dict) -> Slides:
    return Slides.model_validate(data)
