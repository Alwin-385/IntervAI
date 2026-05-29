"use client";

import { motion } from "framer-motion";
import { Brain, Database, FileSearch, Sparkles } from "lucide-react";

import type { AnalysisProgress } from "@/features/resume-analysis/types";

const STEPS = [
  { key: "starting", label: "Preparing context", icon: FileSearch },
  { key: "embeddings", label: "Indexing embeddings", icon: Database },
  { key: "analysis", label: "AI recruiter review", icon: Brain },
  { key: "done", label: "Finalizing scores", icon: Sparkles },
] as const;

function stepIndex(step: string): number {
  if (step === "analysis") return 2;
  if (step === "embeddings") return 1;
  if (step === "done") return 3;
  const idx = STEPS.findIndex((s) => s.key === step);
  if (idx >= 0) return idx;
  if (step === "queued" || step === "starting") return 0;
  return 0;
}

interface AnalysisProgressPanelProps {
  progress: AnalysisProgress | null;
}

export function AnalysisProgressPanel({ progress }: AnalysisProgressPanelProps) {
  const current = stepIndex(progress?.step ?? "starting");
  const percent = progress?.percent ?? 15;

  return (
    <div className="glass-card rounded-2xl border border-primary/20 p-6 md:p-8">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/15">
          <Sparkles className="h-6 w-6 animate-pulse text-primary" />
        </div>
        <div>
          <h2 className="text-lg font-semibold">Analyzing your resume</h2>
          <p className="text-sm text-muted-foreground">
            {progress?.message ?? "Running ATS evaluation and role readiness scoring…"}
          </p>
        </div>
      </div>

      <div className="mb-4 h-2 overflow-hidden rounded-full bg-muted">
        <motion.div
          className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
          initial={{ width: 0 }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 0.4 }}
        />
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {STEPS.map((step, index) => {
          const done = index < current;
          const active = index === current;
          const Icon = step.icon;
          return (
            <div
              key={step.key}
              className={`flex items-center gap-3 rounded-lg border px-3 py-2.5 text-sm ${
                active
                  ? "border-primary/40 bg-primary/10 text-foreground"
                  : done
                    ? "border-border/50 bg-muted/20 text-muted-foreground"
                    : "border-border/30 text-muted-foreground/60"
              }`}
            >
              <Icon className={`h-4 w-4 shrink-0 ${active ? "text-primary" : ""}`} />
              {step.label}
            </div>
          );
        })}
      </div>
    </div>
  );
}
