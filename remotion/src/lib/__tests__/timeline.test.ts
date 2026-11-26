import { describe, it, expect } from 'vitest';
import type { Slide } from '../types';
import { currentSlide, visibleBullets, activeHighlights } from '../timeline';

const slides: Slide[] = [
  {
    index: 0,
    start: 0,
    end: 10,
    chapterLabel: '開場',
    title: '標題一',
    bullets: [
      {
        text: '第一條',
        start: 0,
        end: 5,
        highlight: [{ word: '重點', start: 2, end: 3 }],
      },
    ],
  },
  {
    index: 1,
    start: 10,
    end: 20,
    chapterLabel: '主體',
    title: '標題二',
    bullets: [],
  },
];

it('currentSlide 回傳涵蓋 t 的 slide，缺口回 null', () => {
  expect(currentSlide(slides, 5)?.index).toBe(0);
  expect(currentSlide(slides, 25)).toBeNull();
});

it('visibleBullets 依 start 過濾', () => {
  expect(visibleBullets(slides[0], 1)).toHaveLength(1);
  expect(visibleBullets(slides[0], -1)).toHaveLength(0);
});

it('activeHighlights 依 [start,end) 判斷，越界 highlight 不拋錯', () => {
  expect(activeHighlights(slides[0], 2.5).map((h) => h.word)).toEqual(['重點']);
  expect(() => activeHighlights(slides[0], 99)).not.toThrow();
});
