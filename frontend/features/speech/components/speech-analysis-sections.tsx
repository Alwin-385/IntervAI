"use client";

import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Gauge, Lightbulb, MessageSquareQuote, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { StructuredSpeechAnalysis } from "@/features/speech/types";

function SectionCard({
  title,
  icon,
  children,
  delay,
}: {
  title: string;
  icon: ReactNode;
  children: React.ReactNode;
  delay: number;
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="glass-card rounded-xl border border-border/50 p-5"
    >
      <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold">
        {icon}
        {title}
      </h3>
      {children}
    </motion.section>
  );
}

interface SpeechAnalysisSectionsProps {
  analysis: StructuredSpeechAnalysis;
}

export function SpeechAnalysisSections({ analysis }: SpeechAnalysisSectionsProps) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-2">
        <SectionCard
          title="Delivery metrics"
          icon={<Gauge className="h-4 w-4 text-primary" />}
          delay={0.1}
        >
          <ul className="space-y-3 text-sm">
            <li className="flex justify-between rounded-md bg-muted/20 px-3 py-2">
              <span className="text-muted-foreground">Words per minute</span>
              <span className="font-medium tabular-nums">
                {Math.round(analysis.delivery.words_per_minute)}
              </span>
            </li>
            <li className="flex justify-between rounded-md bg-muted/20 px-3 py-2">
              <span className="text-muted-foreground">Pace</span>
              <span className="font-medium">{analysis.delivery.pace_label}</span>
            </li>
            <li className="flex justify-between rounded-md bg-muted/20 px-3 py-2">
              <span className="text-muted-foreground">Pauses detected</span>
              <span className="font-medium tabular-nums">{analysis.delivery.pause_count}</span>
            </li>
            <li className="flex justify-between rounded-md bg-muted/20 px-3 py-2">
              <span className="text-muted-foreground">Hesitations</span>
              <span className="font-medium tabular-nums">{analysis.delivery.hesitation_count}</span>
            </li>
            {analysis.word_count > 0 && (
              <li className="flex justify-between rounded-md bg-muted/20 px-3 py-2">
                <span className="text-muted-foreground">Word count</span>
                <span className="font-medium tabular-nums">{analysis.word_count}</span>
              </li>
            )}
          </ul>
          {analysis.filler_breakdown.length > 0 && (
            <div className="mt-4">
              <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
                Filler words
              </p>
              <div className="flex flex-wrap gap-1.5">
                {analysis.filler_breakdown.map((f) => (
                  <Badge key={f.word} variant="outline" className="text-xs font-normal">
                    {f.word} × {f.count}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </SectionCard>

        <SectionCard
          title="Strengths"
          icon={<Sparkles className="h-4 w-4 text-emerald-500" />}
          delay={0.15}
        >
          <ul className="space-y-2 text-sm text-foreground/90">
            {analysis.strengths.map((item) => (
              <li key={item} className="rounded-md bg-emerald-500/10 px-3 py-2 leading-snug">
                {item}
              </li>
            ))}
          </ul>
        </SectionCard>
      </div>

      {analysis.weak_patterns.length > 0 && (
        <SectionCard
          title="Areas to improve"
          icon={<AlertTriangle className="h-4 w-4 text-amber-500" />}
          delay={0.2}
        >
          <ul className="space-y-2 text-sm text-foreground/90">
            {analysis.weak_patterns.map((item) => (
              <li key={item} className="rounded-md bg-amber-500/10 px-3 py-2 leading-snug">
                {item}
              </li>
            ))}
          </ul>
        </SectionCard>
      )}

      {analysis.communication_tips.length > 0 && (
        <SectionCard
          title="Communication tips"
          icon={<Lightbulb className="h-4 w-4 text-primary" />}
          delay={0.25}
        >
          <ul className="space-y-2 text-sm text-foreground/90">
            {analysis.communication_tips.map((tip) => (
              <li key={tip} className="flex gap-2 rounded-md bg-muted/20 px-3 py-2 leading-snug">
                <MessageSquareQuote className="mt-0.5 h-4 w-4 shrink-0 text-primary/80" />
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </SectionCard>
      )}
    </div>
  );
}
