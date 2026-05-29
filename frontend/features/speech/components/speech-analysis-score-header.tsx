"use client";

import { motion } from "framer-motion";

import type { StructuredSpeechAnalysis } from "@/features/speech/types";

interface ScoreCardProps {
  label: string;
  value: number;
  delay?: number;
  highlight?: boolean;
  suffix?: string;
}

function ScoreCard({ label, value, delay = 0, highlight, suffix = "%" }: ScoreCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`rounded-xl border p-4 ${
        highlight ? "border-primary/40 bg-primary/10" : "border-border/50 bg-muted/15"
      }`}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className={`mt-2 text-3xl font-bold tabular-nums ${highlight ? "text-primary" : ""}`}>
        {suffix === "%" ? Math.round(value) : value}
        <span className="text-lg font-normal text-muted-foreground"> {suffix}</span>
      </p>
    </motion.div>
  );
}

interface SpeechAnalysisScoreHeaderProps {
  analysis: StructuredSpeechAnalysis;
}

export function SpeechAnalysisScoreHeader({ analysis }: SpeechAnalysisScoreHeaderProps) {
  const { scores, delivery } = analysis;
  return (
    <div className="space-y-3">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <ScoreCard label="Communication" value={scores.communication_score} delay={0} highlight />
        <ScoreCard label="Fluency" value={scores.fluency_score} delay={0.05} highlight />
        <ScoreCard label="Confidence" value={scores.confidence_score} delay={0.1} highlight />
        <ScoreCard
          label="Speaking pace"
          value={scores.speaking_speed_score}
          delay={0.15}
          highlight
        />
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <ScoreCard label="Pause control" value={scores.pause_score} delay={0.2} />
        <ScoreCard
          label="Words per minute"
          value={Math.round(delivery.words_per_minute)}
          delay={0.25}
          suffix="wpm"
        />
        <ScoreCard
          label="Filler words"
          value={delivery.filler_word_count}
          delay={0.3}
          suffix="total"
        />
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="rounded-xl border border-border/50 bg-muted/15 p-4"
        >
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Pace</p>
          <p className="mt-2 text-2xl font-bold">{delivery.pace_label}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            {delivery.pause_count} pauses · {delivery.hesitation_count} hesitations
          </p>
        </motion.div>
      </div>
    </div>
  );
}
