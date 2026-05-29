"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Route,
  RefreshCw,
  Loader2,
  Sparkles,
  CheckCircle2,
  Target,
  BrainCircuit,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useInterviewSessions } from "@/features/interviews/hooks/use-interview-sessions";
import { RoadmapPhaseSection } from "@/features/roadmap/components/roadmap-phase-section";
import { useRoadmap, useGenerateRoadmap, useUpdateRoadmapItem } from "@/features/roadmap/hooks/use-roadmap";
import type { GeneratedRoadmap } from "@/features/roadmap/types";

function OverallProgress({ roadmap }: { roadmap: GeneratedRoadmap }) {
  const allItems = roadmap.phases.flatMap((p) => p.items);
  const completedCount = allItems.filter((i) => i.completed).length;
  const total = allItems.length;
  const pct = total === 0 ? 0 : Math.round((completedCount / total) * 100);

  return (
    <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
      <Card className="glass-card border-primary/20 mb-6">
        <CardContent className="p-5">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 border border-primary/20 shrink-0">
              <BrainCircuit className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-primary uppercase tracking-widest mb-1">
                AI Career Coach
              </p>
              <h2 className="text-base font-bold text-foreground leading-snug">
                {roadmap.title}
              </h2>
              <p className="text-sm text-muted-foreground mt-1 leading-relaxed">
                {roadmap.summary}
              </p>
            </div>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3 mt-5">
            <div className="rounded-lg bg-muted/30 px-3 py-2 text-center">
              <p className="text-lg font-bold text-foreground">{completedCount}</p>
              <p className="text-xs text-muted-foreground">Completed</p>
            </div>
            <div className="rounded-lg bg-muted/30 px-3 py-2 text-center">
              <p className="text-lg font-bold text-foreground">{total - completedCount}</p>
              <p className="text-xs text-muted-foreground">Remaining</p>
            </div>
            <div className="rounded-lg bg-muted/30 px-3 py-2 text-center">
              <p className="text-lg font-bold text-foreground">{roadmap.phases.length}</p>
              <p className="text-xs text-muted-foreground">Phases</p>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-4">
            <div className="flex justify-between text-xs text-muted-foreground mb-1.5">
              <span>Overall progress</span>
              <span className="font-semibold text-foreground">{pct}%</span>
            </div>
            <Progress value={pct} className="h-2" />
          </div>

          {/* Addressed weak areas */}
          {roadmap.weak_areas_addressed.length > 0 && (
            <div className="mt-4">
              <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1.5">
                <Target className="h-3 w-3" />
                Targeting your weak areas
              </p>
              <div className="flex flex-wrap gap-1.5">
                {roadmap.weak_areas_addressed.map((kind, i) => (
                  <span
                    key={`${kind}-${i}`}
                    className="rounded-full bg-accent/10 border border-accent/20 px-2 py-0.5 text-xs text-accent"
                  >
                    {kind.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

function EmptyState({
  onGenerate,
  isGenerating,
  attendedRoles,
  selectedRole,
  onSelectRole,
}: {
  onGenerate: () => void;
  isGenerating: boolean;
  attendedRoles: string[];
  selectedRole?: string;
  onSelectRole: (role?: string) => void;
}) {
  return (
    <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}>
      <Card className="glass-card border-border/50 max-w-xl mx-auto mt-12">
        <CardHeader className="text-center pb-3">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 border border-primary/20 mb-4">
            <Sparkles className="h-7 w-7 text-primary" />
          </div>
          <CardTitle className="text-xl">Your AI roadmap is one click away</CardTitle>
          <CardDescription className="text-base mt-1">
            IntervAI will analyze your interview history, detect recurring weak areas, and build a
            personalized 3-phase improvement plan — like having an AI career coach.
          </CardDescription>
        </CardHeader>
        <CardContent className="pb-6">
          {attendedRoles.length > 0 && (
            <div className="mb-4 flex flex-wrap justify-center gap-2">
              <Button
                variant={selectedRole ? "outline" : "default"}
                size="sm"
                onClick={() => onSelectRole(undefined)}
              >
                All fields
              </Button>
              {attendedRoles.map((role) => (
                <Button
                  key={role}
                  variant={selectedRole === role ? "default" : "outline"}
                  size="sm"
                  onClick={() => onSelectRole(role)}
                >
                  {role}
                </Button>
              ))}
            </div>
          )}
          <div className="flex justify-center">
          <Button
            size="lg"
            onClick={onGenerate}
            disabled={isGenerating}
            className="gap-2 px-8"
          >
            {isGenerating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            {isGenerating ? "Generating roadmap…" : "Generate my roadmap"}
          </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export function RoadmapPageContent() {
  const [selectedRole, setSelectedRole] = useState<string | undefined>(undefined);
  const { data: sessionsData } = useInterviewSessions(1, 100);
  const attendedRoles = Array.from(
    new Set((sessionsData?.items ?? []).map((s) => s.target_role).filter(Boolean)),
  );

  const { data: roadmap, isLoading } = useRoadmap(selectedRole);
  const generateMutation = useGenerateRoadmap();
  const updateMutation = useUpdateRoadmapItem(roadmap?.id ?? "", selectedRole);
  const [pendingItemId, setPendingItemId] = useState<string | undefined>(undefined);

  async function handleToggle(itemId: string, completed: boolean) {
    setPendingItemId(itemId);
    try {
      await updateMutation.mutateAsync({ itemId, completed });
    } finally {
      setPendingItemId(undefined);
    }
  }

  async function handleGenerate() {
    await generateMutation.mutateAsync(selectedRole);
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!roadmap) {
    return (
      <EmptyState
        onGenerate={handleGenerate}
        isGenerating={generateMutation.isGenerating}
        attendedRoles={attendedRoles}
        selectedRole={selectedRole}
        onSelectRole={setSelectedRole}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Route className="h-6 w-6 text-primary" />
            Improvement Roadmap
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            {roadmap.target_role ? `Field: ${roadmap.target_role} · ` : ""}
            Last generated {new Date(roadmap.generated_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Button
            variant={selectedRole ? "outline" : "default"}
            size="sm"
            onClick={() => setSelectedRole(undefined)}
          >
            All fields
          </Button>
          {attendedRoles.map((role) => (
            <Button
              key={role}
              variant={selectedRole === role ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedRole(role)}
            >
              {role}
            </Button>
          ))}
          <Button
            variant="outline"
            size="sm"
            onClick={handleGenerate}
            disabled={generateMutation.isGenerating}
            className="gap-2"
          >
            {generateMutation.isGenerating ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <RefreshCw className="h-3.5 w-3.5" />
            )}
            Regenerate
          </Button>
        </div>
      </div>

      {/* Overall progress card */}
      <OverallProgress roadmap={roadmap} />

      <div className="rounded-md border border-border/40 bg-muted/20 px-3 py-2 text-xs text-muted-foreground">
        Showing roadmap for:{" "}
        <span className="font-semibold text-foreground">
          {selectedRole ?? roadmap.target_role ?? "All fields"}
        </span>
      </div>

      {/* Phase timeline */}
      <div className="space-y-10">
        {roadmap.phases.map((phase, idx) => (
          <RoadmapPhaseSection
            key={phase.phase}
            phase={phase}
            roadmapId={roadmap.id}
            onToggle={handleToggle}
            pendingItemId={pendingItemId}
            index={idx}
          />
        ))}
      </div>

      {/* All done banner */}
      {roadmap.phases.length > 0 &&
        roadmap.phases.every((p) => p.items.every((i) => i.completed)) && (
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            className="rounded-xl border border-green-500/30 bg-green-500/10 p-5 text-center"
          >
            <CheckCircle2 className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <p className="font-semibold text-green-400">All tasks complete!</p>
            <p className="text-sm text-muted-foreground mt-1">
              Amazing work. Regenerate your roadmap for the next level of improvements.
            </p>
          </motion.div>
        )}
    </div>
  );
}
