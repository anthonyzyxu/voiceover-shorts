import React from 'react';
import {Composition} from 'remotion';
import {Video} from './Video';
import slidesData from '../../slides.json';
import transcriptData from '../../transcript.json';
import type {Slides, Transcript} from './lib/types';

const slides = slidesData as Slides;
const transcript = transcriptData as Transcript;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Main"
      component={Video}
      durationInFrames={Math.max(30, Math.round(slides.duration * 30))}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        slides,
        transcript,
        videoSrc: 'input.mov',
        audioSrc: 'input.mov',
      }}
    />
  );
};
