"use client";

import { motion } from "framer-motion";

import { cn } from "@/lib/utils";

interface AudioWaveformProps {
  levels: number[];
  isActive: boolean;
  className?: string;
}

export function AudioWaveform({ levels, isActive, className }: AudioWaveformProps) {
  const bars = levels.length > 0 ? levels : Array.from({ length: 32 }, () => 0.08);

  return (
    <div
      className={cn(
        "flex h-20 items-end justify-center gap-1 rounded-xl border border-border/60 bg-muted/20 px-4 py-3",
        className,
      )}
      aria-hidden
    >
      {bars.map((level, i) => (
        <motion.div
          key={i}
          className={cn(
            "w-1.5 rounded-full",
            isActive ? "bg-primary" : "bg-muted-foreground/40",
          )}
          animate={{ height: `${Math.max(8, level * 72)}px` }}
          transition={{ duration: 0.08, ease: "easeOut" }}
        />
      ))}
    </div>
  );
}
