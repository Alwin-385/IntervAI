"use client";

import { motion } from "framer-motion";
import { BarChart3, TrendingUp } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const barHeights = [40, 65, 45, 80, 55, 72, 48, 90, 60, 75, 52, 85];

export function AnalyticsPlaceholder() {
  return (
    <Card className="glass-card h-full border-border/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Interview analytics
        </CardTitle>
        <CardDescription>Score trends across sessions (coming soon)</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex h-52 items-end justify-between gap-1.5 rounded-xl border border-border/40 bg-muted/20 px-4 pb-4 pt-8">
          {barHeights.map((height, index) => (
            <motion.div
              key={index}
              initial={{ scaleY: 0 }}
              whileInView={{ scaleY: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.04 }}
              className="w-full max-w-[28px] origin-bottom rounded-t-md bg-gradient-to-t from-primary/80 to-accent/60"
              style={{ height: `${height}%` }}
            />
          ))}
        </div>
        <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
          <TrendingUp className="h-4 w-4 text-emerald-400" />
          Recharts integration in a future phase
        </div>
      </CardContent>
    </Card>
  );
}
