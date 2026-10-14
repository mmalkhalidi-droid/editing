import React from "react";
import { COLORS } from "../config";

export const CheckIcon: React.FC<{ size?: number; progress?: number }> = ({
  size = 72,
  progress = 1,
}) => {
  // Check path length ~ 40 in a 48 viewBox
  const len = 40;
  return (
    <svg width={size} height={size} viewBox="0 0 48 48">
      <circle cx="24" cy="24" r="22" fill={COLORS.accent} />
      <path
        d="M14 25 L21 32 L35 17"
        fill="none"
        stroke={COLORS.onAccent}
        strokeWidth={5}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={len}
        strokeDashoffset={len * (1 - progress)}
      />
    </svg>
  );
};

export const ChatIcon: React.FC<{ size?: number; color?: string }> = ({
  size = 56,
  color = "#fff",
}) => (
  <svg width={size} height={size} viewBox="0 0 48 48">
    <path
      d="M24 5C13.5 5 5 13 5 23c0 3.6 1.1 7 3 9.8L6 42l9.6-2.6C18.1 40.8 21 41.5 24 41.5c10.5 0 19-8 19-18.2S34.5 5 24 5z"
      fill="none"
      stroke={color}
      strokeWidth={3.5}
      strokeLinejoin="round"
    />
    <path
      d="M17.5 15.5c.6-.6 1.6-.6 2.1.1l2.1 3c.4.6.3 1.4-.2 1.9l-1.2 1.1c1.2 2.6 3.2 4.6 5.8 5.9l1.1-1.2c.5-.5 1.3-.6 1.9-.2l3 2.1c.7.5.8 1.5.2 2.1l-1.4 1.5c-1 1-2.6 1.4-4 .8-5.4-2.1-9.7-6.4-11.8-11.8-.5-1.4-.2-3 .8-4z"
      fill={color}
    />
  </svg>
);
