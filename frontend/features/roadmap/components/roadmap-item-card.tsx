"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircle2,
  Circle,
  ChevronDown,
  Clock,
  BookOpen,
  Lightbulb,
  ExternalLink,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { RoadmapPriorityBadge } from "@/features/roadmap/components/roadmap-priority-badge";
import type { RoadmapItem } from "@/features/roadmap/types";

interface Props {
  item: RoadmapItem;
  onToggle: (itemId: string, completed: boolean) => void;
  isPending?: boolean;
}

export function RoadmapItemCard({ item, onToggle, isPending }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card
      className={`glass-card transition-all duration-200 ${
        item.completed ? "opacity-60 border-border/30" : "border-border/50 hover:border-primary/40"
      }`}
    >
      <CardContent className="p-4">
        {/* Header row */}
        <div className="flex items-start gap-3">
          {/* Completion toggle */}
          <button
            onClick={() => onToggle(item.id, !item.completed)}
            disabled={isPending}
            className="mt-0.5 shrink-0 text-muted-foreground hover:text-primary transition-colors disabled:opacity-50"
            aria-label={item.completed ? "Mark incomplete" : "Mark complete"}
          >
            {item.completed ? (
              <CheckCircle2 className="h-5 w-5 text-green-500" />
            ) : (
              <Circle className="h-5 w-5" />
            )}
          </button>

          {/* Title + badges */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <span
                className={`text-sm font-semibold ${item.completed ? "line-through text-muted-foreground" : "text-foreground"}`}
              >
                {item.title}
              </span>
              <RoadmapPriorityBadge priority={item.priority} />
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {item.estimated_time}
              </span>
              {item.category && (
                <span className="rounded-full bg-muted/40 px-2 py-0.5">{item.category}</span>
              )}
            </div>
          </div>

          {/* Expand toggle */}
          <button
            onClick={() => setExpanded((e) => !e)}
            className="shrink-0 text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Toggle details"
          >
            <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
              <ChevronDown className="h-4 w-4" />
            </motion.div>
          </button>
        </div>

        {/* Expanded details */}
        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="mt-4 space-y-3 pl-8 text-sm">
                <p className="text-muted-foreground leading-relaxed">{item.description}</p>

                <div className="flex items-start gap-2 rounded-lg bg-primary/5 border border-primary/20 p-3">
                  <Lightbulb className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                  <div>
                    <p className="text-xs font-semibold text-primary mb-1">Practice recommendation</p>
                    <p className="text-xs text-muted-foreground">{item.practice_recommendation}</p>
                  </div>
                </div>

                {item.resources.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-muted-foreground mb-1.5 flex items-center gap-1.5">
                      <BookOpen className="h-3 w-3" />
                      Resources
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {item.resources.map((r, i) => (
                        <span
                          key={`${item.id}-resource-${i}`}
                          className="inline-flex items-center gap-1 rounded-md bg-muted/40 px-2 py-0.5 text-xs text-muted-foreground"
                        >
                          <ExternalLink className="h-2.5 w-2.5" />
                          {r}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {item.completed && item.completed_at && (
                  <p className="text-xs text-green-500/80">
                    Completed {new Date(item.completed_at).toLocaleDateString()}
                  </p>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
}
