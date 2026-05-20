"use client";

import { motion } from "framer-motion";
import {
  Calendar,
  FileText,
  Mic,
  TrendingUp,
  type LucideIcon,
} from "lucide-react";

import { AnimatedCounter } from "@/components/motion/animated-counter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface StatItem {
  label: string;
  value: number;
  suffix?: string;
  decimals?: number;
  icon: LucideIcon;
  change: string;
  trend?: "up" | "neutral";
}

const stats: StatItem[] = [
  {
    label: "Mock interviews",
    value: 0,
    icon: Mic,
    change: "Start your first session",
    trend: "neutral",
  },
  {
    label: "Resumes analyzed",
    value: 0,
    icon: FileText,
    change: "Upload a resume",
    trend: "neutral",
  },
  {
    label: "Average score",
    value: 0,
    suffix: "%",
    icon: TrendingUp,
    change: "No sessions yet",
    trend: "neutral",
  },
  {
    label: "Practice hours",
    value: 0,
    suffix: "h",
    decimals: 1,
    icon: Calendar,
    change: "This week",
    trend: "up",
  },
];

interface StatsGridProps {
  isLoading?: boolean;
}

export function StatsGrid({ isLoading }: StatsGridProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="glass-card border-border/50">
            <CardHeader className="pb-2">
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16" />
              <Skeleton className="mt-2 h-3 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.06 }}
        >
          <Card className="glass-card border-border/50 transition-colors hover:border-primary/30">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.label}
              </CardTitle>
              <div className="rounded-lg bg-primary/10 p-2">
                <stat.icon className="h-4 w-4 text-primary" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold tracking-tight">
                <AnimatedCounter
                  value={stat.value}
                  suffix={stat.suffix}
                  decimals={stat.decimals ?? 0}
                  delay={index * 0.08}
                />
              </p>
              <p className="mt-1 text-xs text-muted-foreground">{stat.change}</p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
