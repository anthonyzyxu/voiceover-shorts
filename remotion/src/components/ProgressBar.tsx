import React from 'react';

const FONT = '"PingFang TC", "Noto Sans TC", sans-serif';

export const ProgressBar: React.FC<{
  current: number;
  total: number;
  label: string;
}> = ({current, total, label}) => {
  const pct = total > 0 ? Math.min(100, (current / total) * 100) : 0;
  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        padding: '60px 64px 0 64px',
        zIndex: 20,
        fontFamily: FONT,
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 14,
        }}
      >
        <span style={{fontSize: 30, fontWeight: 600, color: '#33415c'}}>
          {label}
        </span>
        <span style={{fontSize: 24, color: '#74809a'}}>{Math.round(pct)}%</span>
      </div>
      <div
        style={{
          height: 6,
          borderRadius: 3,
          background: 'rgba(110,130,165,0.2)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #4a7dff, #6aa0ff)',
            borderRadius: 3,
          }}
        />
      </div>
    </div>
  );
};
