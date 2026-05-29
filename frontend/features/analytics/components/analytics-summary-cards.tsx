"use client";

import { motion } from "framer-motion";
import { Award, MessageCircle, Mic, TrendingDown, TrendingUp, Zap } from "lucide-react";

import type { AnalyticsSummary, TrendDirection } from "@/features/analytics/types";

function TrendBadge({ trend, delta }: { trend: TrendDirection; delta: number }) {
  if (trend === "insufficient_data") {
    return <span className="text-xs text-muted-foreground">Not enough data</span>;
  }
  const up = trend === "improving";
  const Icon = up ? TrendingUp : trend === "declining" ? TrendingDown : TrendingUp;
  const color = up ? "text-emerald-400" : trend === "declining" ? "text-red-400" : "text-yellow-400";
  return (
    <span className={`inline-flex items-center gap-1 text-xs ${color}`}>
      <Icon className="h-3 w-3" />
      {trend === "stable" ? "Stable" : up ? "Improving" : "Declining"} ({delta > 0 ? "+" : ""}
      {delta})
    </span>
  );
}

interface Props {
  summary: AnalyticsSummary;
}

export function AnalyticsSummaryCards({ summary }: Props) {
  const cards = [
    {
      label: "Average score",
      value: summary.average_score != null ? `${summary.average_score}%` : "—",
      icon: Award,
      extra: <TrendBadge trend={summary.score_trend} delta={summary.score_trend_delta} />,
    },
    {
      label: "Communication",
      value: summary.average_communication != null ? `${summary.average_communication}%` : "—",
      icon: MessageCircle,
    },
    {
      label: "Confidence",
      value: summary.average_confidence != null ? `${summary.average_confidence}%` : "—",
      icon: Mic,
    },
    {
      label: "Technical",
      value: summary.average_technical != null ? `${summary.average_technical}%` : "—",
      icon: Zap,
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card, i) => {
        const Icon = card.icon;
        return (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="glass-card rounded-xl border border-border/50 p-4"
          >
            <div className="flex items-center justify-between">
              <p className="text-xs font-medium text-muted-foreground">{card.label}</p>
              <Icon className="h-4 w-4 text-primary" />
            </div>
            <p className="mt-2 text-2xl font-bold">{card.value}</p>
            {card.extra && <div className="mt-2">{card.extra}</div>}
          </motion.div>
        );
      })}
    </div>
  );
}
