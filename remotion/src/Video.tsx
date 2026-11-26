import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame} from 'remotion';
import {Background} from './components/Background';
import {PiP} from './components/PiP';
import {ProgressBar} from './components/ProgressBar';
import {Slide} from './components/Slide';
import {currentSlide} from './lib/timeline';
import type {Slides, Transcript} from './lib/types';

type VideoProps = {
  slides: Slides;
  transcript: Transcript;
  videoSrc: string;
  audioSrc?: string;
};

export const Video: React.FC<VideoProps> = ({
  slides,
  transcript,
  videoSrc,
  audioSrc,
}) => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const slide = currentSlide(slides.slides, t);

  // transcript 保留供後續音軌對齊使用（本步先接 slides）。
  void transcript;

  return (
    <AbsoluteFill
      style={{fontFamily: '"PingFang TC", "Noto Sans TC", sans-serif'}}
    >
      <Background />
      <ProgressBar
        current={t}
        total={slides.duration}
        label={slide ? slide.chapterLabel : ''}
      />
      {slide ? <Slide slide={slide} t={t} /> : null}
      <PiP src={staticFile(videoSrc)} width={380} height={640} />
      {audioSrc ? <Audio src={staticFile(audioSrc)} /> : null}
    </AbsoluteFill>
  );
};
