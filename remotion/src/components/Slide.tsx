import React from 'react';
import type {Bullet, Slide as SlideData} from '../lib/types';
import {activeHighlights, visibleBullets} from '../lib/timeline';

const FONT = '"PingFang TC", "Noto Sans TC", sans-serif';

const easeOutCubic = (x: number) => 1 - Math.pow(1 - x, 3);

const anim = (t: number, start: number, dur: number): number => {
  if (t < start) {
    return 0;
  }
  return easeOutCubic(Math.min(1, (t - start) / dur));
};

function highlightText(text: string, active: Set<string>): React.ReactNode {
  if (active.size === 0) {
    return text;
  }
  const words = [...active].sort((a, b) => b.length - a.length);
  const escaped = words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const regex = new RegExp(`(${escaped.join('|')})`, 'g');
  return text.split(regex).map((part, i) =>
    active.has(part) ? (
      <span
        key={i}
        style={{
          background: '#ffe08a',
          color: '#7a4d00',
          borderRadius: 6,
          padding: '0 4px',
          fontWeight: 700,
        }}
      >
        {part}
      </span>
    ) : (
      <span key={i}>{part}</span>
    ),
  );
}

export const Slide: React.FC<{slide: SlideData; t: number}> = ({slide, t}) => {
  const bullets = visibleBullets(slide, t);
  const active = new Set(activeHighlights(slide, t).map((h) => h.word));

  const titleP = anim(t, slide.start, 0.5);
  const titleStyle: React.CSSProperties = {
    fontSize: 64,
    fontWeight: 700,
    lineHeight: 1.25,
    color: '#1f2a44',
    opacity: titleP,
    transform: `translateY(${(1 - titleP) * 28}px)`,
    fontFamily: FONT,
  };

  return (
    <div
      style={{
        position: 'absolute',
        left: 80,
        right: 460,
        top: 420,
      }}
    >
      <div style={titleStyle}>{slide.title}</div>
      <ul style={{listStyle: 'none', margin: 0, padding: 0, marginTop: 56}}>
        {bullets.map((b: Bullet, i: number) => {
          const p = anim(t, b.start, 0.4);
          return (
            <li
              key={i}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                marginBottom: 30,
                fontSize: 40,
                fontWeight: 500,
                lineHeight: 1.4,
                color: '#2c3a5c',
                opacity: p,
                transform: `translateY(${(1 - p) * 22}px)`,
                fontFamily: FONT,
              }}
            >
              <span style={{color: '#4a7dff', fontWeight: 700, marginRight: 18}}>
                •
              </span>
              <span>{highlightText(b.text, active)}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
