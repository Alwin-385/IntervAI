"use client";

import { motion } from "framer-motion";
import { Lightbulb, Target } from "lucide-react";

import { PriorityBadge } from "@/features/weak-areas/components/priority-badge";
import { TrendIndicator } from "@/features/weak-areas/components/trend-indicator";
import type { DetectedWeakArea } from "@/features/weak-areas/types";

interface WeakAreaCardProps {
  area: DetectedWeakArea;
  index?: number;
}

export function WeakAreaCard({ area, index = 0 }: WeakAreaCardProps) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      className="glass-card rounded-xl border border-border/50 p-5"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <Target className="h-4 w-4 text-primary" />
            <h3 className="font-semibold">{area.area_name}</h3>
            <PriorityBadge priority={area.priority} />
          </div>
          <p className="text-xs text-muted-foreground">{area.category}</p>
        </div>
        <TrendIndicator trend={area.trend} delta={area.trend_delta} />
      </div>

      <p className="mt-3 text-sm text-muted-foreground">{area.description}</p>

      <div className="mt-4 flex flex-wrap gap-4 text-sm">
        <div>
          <p className="text-xs uppercase text-muted-foreground">Frequency</p>
          <p className="font-medium tabular-nums">{area.frequency_label}</p>
        </div>
        <div>
          <p className="text-xs uppercase text-muted-foreground">Rate</p>
          <p className="font-medium tabular-nums">{Math.round(area.frequency_rate * 100)}%</p>
        </div>
      </div>

      {area.evidence.length > 0 && (
        <ul className="mt-3 space-y-1 text-xs text-muted-foreground">
          {area.evidence.map((e, evidenceIndex) => (
            <li key={`${area.kind}-evidence-${evidenceIndex}`}>• {e}</li>
          ))}
        </ul>
      )}

      <div className="mt-4 space-y-2">
        <p className="flex items-center gap-1.5 text-xs font-semibold uppercase text-muted-foreground">
          <Lightbulb className="h-3.5 w-3.5" />
          Improvements
        </p>
        <ul className="space-y-1.5 text-sm">
          {area.improvement_suggestions.slice(0, 3).map((tip, tipIndex) => (
            <li key={`${area.kind}-tip-${tipIndex}`} className="rounded-md bg-muted/25 px-3 py-2">
              {tip}
            </li>
          ))}
        </ul>
      </div>

      {area.practice_recommendations.length > 0 && (
        <p className="mt-3 text-xs text-muted-foreground">
          <span className="font-medium text-foreground">Practice: </span>
          {area.practice_recommendations[0]}
        </p>
      )}
    </motion.article>
  );
}
