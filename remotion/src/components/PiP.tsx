import React from 'react';
import {OffthreadVideo, useCurrentFrame} from 'remotion';

export const PiP: React.FC<{src: string; width: number; height: number}> = ({
  src,
  width,
  height,
}) => {
  const frame = useCurrentFrame();
  const breath = 0.5 + 0.5 * Math.sin((frame / 30) * 2 * Math.PI * (1 / 3));
  return (
    <div
      style={{
        position: 'absolute',
        top: 120,
        right: 40,
        width,
        height,
        borderRadius: 20,
        overflow: 'hidden',
        boxShadow: '0 8px 32px rgba(28,40,66,0.28)',
        border: `${2 + breath * 3}px solid rgba(74,125,255,${
          0.35 + breath * 0.35
        })`,
      }}
    >
      <OffthreadVideo
        src={src}
        style={{width: '100%', height: '100%', objectFit: 'cover'}}
      />
    </div>
  );
};
