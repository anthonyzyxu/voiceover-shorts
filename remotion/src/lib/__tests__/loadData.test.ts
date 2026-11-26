import {describe, it, expect} from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {loadSlides, loadTranscript} from '../loadData';

function writeTemp(name: string, content: object): string {
  const p = path.join(os.tmpdir(), `remotion-${name}-${Date.now()}-${Math.random()}.json`);
  fs.writeFileSync(p, JSON.stringify(content));
  return p;
}

describe('loadSlides', () => {
  it('載入合法 slides.json', () => {
    const p = writeTemp('slides', {title: '主題', duration: 10, slides: []});
    const s = loadSlides(p);
    expect(s.duration).toBe(10);
    fs.unlinkSync(p);
  });

  it('缺 duration 欄拋錯', () => {
    const p = writeTemp('slides-bad', {title: '主題', slides: []});
    expect(() => loadSlides(p)).toThrow();
    fs.unlinkSync(p);
  });
});

describe('loadTranscript', () => {
  it('載入合法 transcript.json', () => {
    const p = writeTemp('transcript', {
      audio_file: 'a.wav',
      language: 'zh',
      model: 'x',
      segments: [],
    });
    const t = loadTranscript(p);
    expect(t.segments).toEqual([]);
    fs.unlinkSync(p);
  });

  it('缺 segments 拋錯', () => {
    const p = writeTemp('transcript-bad', {audio_file: 'a.wav'});
    expect(() => loadTranscript(p)).toThrow();
    fs.unlinkSync(p);
  });
});
