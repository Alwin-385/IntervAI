"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Target } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const sampleAreas = [
  { name: "System design depth", severity: "high" as const, category: "Technical" },
  { name: "STAR storytelling", severity: "medium" as const, category: "Behavioral" },
  { name: "Speaking pace", severity: "low" as const, category: "Delivery" },
];

const severityStyles = {
  high: "border-amber-500/30 bg-amber-500/10 text-amber-400",
  medium: "border-primary/30 bg-primary/10 text-primary",
  low: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
};

export function WeakAreasPreview() {
  return (
    <Card className="glass-card h-full border-border/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5 text-accent" />
          Weak areas
        </CardTitle>
        <CardDescription>Focus zones identified from practice</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {sampleAreas.map((area, index) => (
          <motion.div
            key={area.name}
            initial={{ opacity: 0, x: 8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.08 }}
            className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/20 px-4 py-3"
          >
            <div>
              <p className="text-sm font-medium">{area.name}</p>
              <p className="text-xs text-muted-foreground">{area.category}</p>
            </div>
            <Badge variant="outline" className={severityStyles[area.severity]}>
              {area.severity}
            </Badge>
          </motion.div>
        ))}
        <div className="flex items-start gap-2 rounded-lg border border-dashed border-border/60 p-3 text-xs text-muted-foreground">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          Sample preview — real weak areas appear after resume analysis and interviews.
        </div>
      </CardContent>
    </Card>
  );
}
