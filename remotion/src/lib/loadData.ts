import fs from 'node:fs';
import type {Slides, Transcript} from './types';

export function loadSlides(path: string): Slides {
  const data = JSON.parse(fs.readFileSync(path, 'utf-8'));
  if (typeof data?.duration !== 'number' || !Array.isArray(data?.slides)) {
    throw new Error(`slides.json 格式錯誤：缺少 duration 或 slides（${path}）`);
  }
  return data as Slides;
}

export function loadTranscript(path: string): Transcript {
  const data = JSON.parse(fs.readFileSync(path, 'utf-8'));
  if (!Array.isArray(data?.segments)) {
    throw new Error(`transcript.json 格式錯誤：缺少 segments（${path}）`);
  }
  return data as Transcript;
}
