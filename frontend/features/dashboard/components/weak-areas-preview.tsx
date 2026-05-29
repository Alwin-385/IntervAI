"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { AlertTriangle, Loader2, Target } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useWeakAreasAnalytics } from "@/features/weak-areas/hooks/use-weak-areas-analytics";

const priorityStyles = {
  high: "border-red-500/30 bg-red-500/10 text-red-400",
  medium: "border-amber-500/30 bg-amber-500/10 text-amber-400",
  low: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
};

export function WeakAreasPreview() {
  const { data, isLoading } = useWeakAreasAnalytics();
  const top = data?.weak_areas.slice(0, 3) ?? [];

  return (
    <Card className="glass-card h-full border-border/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5 text-accent" />
          Weak areas
        </CardTitle>
        <CardDescription>From interview answer & speech history</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading && (
          <div className="flex justify-center py-6">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}
        {!isLoading &&
          top.map((area, index) => (
            <motion.div
              key={area.kind}
              initial={{ opacity: 0, x: 8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.08 }}
              className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/20 px-4 py-3"
            >
              <div>
                <p className="text-sm font-medium">{area.area_name}</p>
                <p className="text-xs text-muted-foreground">{area.frequency_label}</p>
              </div>
              <Badge variant="outline" className={priorityStyles[area.priority]}>
                {area.priority}
              </Badge>
            </motion.div>
          ))}
        {!isLoading && top.length === 0 && (
          <div className="flex items-start gap-2 rounded-lg border border-dashed border-border/60 p-3 text-xs text-muted-foreground">
            <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
            Complete interviews to detect recurring weaknesses.
          </div>
        )}
        <Button asChild variant="outline" size="sm" className="w-full">
          <Link href="/dashboard/weak-areas">View all weak areas</Link>
        </Button>
      </CardContent>
    </Card>
  );
}
