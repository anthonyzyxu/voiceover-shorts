export interface Highlight {
  word: string;
  start: number;
  end: number;
}

export interface Bullet {
  text: string;
  start: number;
  end: number;
  highlight: Highlight[];
}

export interface Slide {
  index: number;
  start: number;
  end: number;
  chapterLabel: string;
  title: string;
  bullets: Bullet[];
}

export interface Slides {
  title: string;
  duration: number;
  slides: Slide[];
}

export interface Word {
  word: string;
  start: number;
  end: number;
}

export interface Segment {
  id: number;
  start: number;
  end: number;
  text: string;
  words: Word[];
}

export interface Transcript {
  audio_file: string;
  language: string;
  model: string;
  segments: Segment[];
}
