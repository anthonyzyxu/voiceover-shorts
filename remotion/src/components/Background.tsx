import React from 'react';
import {AbsoluteFill} from 'remotion';

export const Background: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background:
          'linear-gradient(160deg, #f7f9fc 0%, #eef2f7 45%, #e7edf6 100%)',
      }}
    >
      <AbsoluteFill
        style={{
          backgroundImage:
            'linear-gradient(rgba(110,130,165,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(110,130,165,0.07) 1px, transparent 1px)',
          backgroundSize: '48px 48px',
        }}
      />
    </AbsoluteFill>
  );
};
