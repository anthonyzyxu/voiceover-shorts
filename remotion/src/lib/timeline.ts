import type { Bullet, Highlight, Slide } from './types';

export function currentSlide(slides: Slide[], t: number): Slide | null {
  for (const s of slides) {
    if (s.start <= t && t < s.end) {
      return s;
    }
  }
  return null;
}

export function visibleBullets(slide: Slide, t: number): Bullet[] {
  return slide.bullets.filter((b) => b.start <= t);
}

export function activeHighlights(slide: Slide, t: number): Highlight[] {
  const out: Highlight[] = [];
  for (const b of slide.bullets) {
    if (b.start > t) {
      continue;
    }
    for (const h of b.highlight) {
      if (h.start <= t && t < h.end) {
        out.push(h);
      }
    }
  }
  return out;
}
