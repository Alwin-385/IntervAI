"use client";

import { motion } from "framer-motion";
import { Zap, TrendingUp, Star } from "lucide-react";
import { Progress } from "@/components/ui/progress";

import { RoadmapItemCard } from "@/features/roadmap/components/roadmap-item-card";
import type { RoadmapPhase, RoadmapPhaseKind } from "@/features/roadmap/types";

const PHASE_CONFIG: Record<
  RoadmapPhaseKind,
  { icon: React.ElementType; color: string; borderColor: string; dotColor: string }
> = {
  immediate: {
    icon: Zap,
    color: "text-red-400",
    borderColor: "border-red-500/30",
    dotColor: "bg-red-500",
  },
  short_term: {
    icon: TrendingUp,
    color: "text-yellow-400",
    borderColor: "border-yellow-500/30",
    dotColor: "bg-yellow-500",
  },
  advanced: {
    icon: Star,
    color: "text-purple-400",
    borderColor: "border-purple-500/30",
    dotColor: "bg-purple-500",
  },
};

interface Props {
  phase: RoadmapPhase;
  roadmapId: string;
  onToggle: (itemId: string, completed: boolean) => void;
  pendingItemId?: string;
  index: number;
}

export function RoadmapPhaseSection({ phase, roadmapId, onToggle, pendingItemId, index }: Props) {
  const config = PHASE_CONFIG[phase.phase];
  const Icon = config.icon;
  const completed = phase.items.filter((i) => i.completed).length;
  const total = phase.items.length;
  const progressPct = total === 0 ? 0 : Math.round((completed / total) * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      {/* Phase header */}
      <div className="mb-4 flex items-start gap-4">
        <div
          className={`relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 bg-background ${config.borderColor}`}
        >
          <Icon className={`h-5 w-5 ${config.color}`} />
          {/* Timeline connector dot */}
          <span
            className={`absolute -bottom-[calc(100%+4px)] left-1/2 h-full w-0.5 -translate-x-1/2 ${config.dotColor}/30`}
          />
        </div>
        <div className="flex-1 pt-1">
          <div className="flex flex-wrap items-center gap-3">
            <h3 className={`text-base font-bold ${config.color}`}>{phase.title}</h3>
            <span className="rounded-full border border-border/40 bg-muted/30 px-2.5 py-0.5 text-xs text-muted-foreground">
              {phase.estimated_duration}
            </span>
            <span className="text-xs text-muted-foreground">
              {completed}/{total} done
            </span>
          </div>
          <p className="mt-0.5 text-sm text-muted-foreground">{phase.subtitle}</p>
          <div className="mt-2 flex items-center gap-2">
            <Progress value={progressPct} className="h-1.5 max-w-xs flex-1" />
            <span className="text-xs text-muted-foreground">{progressPct}%</span>
          </div>
        </div>
      </div>

      {/* Items */}
      <div className="ml-14 space-y-3">
        {phase.items.map((item) => (
          <RoadmapItemCard
            key={item.id}
            item={item}
            onToggle={onToggle}
            isPending={pendingItemId === item.id}
          />
        ))}
      </div>
    </motion.div>
  );
}
