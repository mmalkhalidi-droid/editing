import React from "react";
import { AbsoluteFill } from "remotion";
import { Background } from "../components/Background";
import { Clock } from "../components/Clock";
import { KineticLine } from "../components/KineticLine";
import { SafeArea } from "../components/SafeArea";
import { COPY } from "../copy";

export const Hook: React.FC = () => (
  <AbsoluteFill>
    <Background />
    <SafeArea gap={30}>
      <Clock size={340} start={4} ticks={15} framesPerTick={3} />
      <KineticLine text={COPY.hook.line1} delay={8} fontSize={104} />
      <KineticLine
        text={COPY.hook.line2}
        delay={40}
        stagger={5}
        fontSize={74}
        fontWeight={800}
      />
    </SafeArea>
  </AbsoluteFill>
);
