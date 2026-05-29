"use client";

import Link from "next/link";
import { ArrowLeft, Trophy } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useInterviewRuntime } from "@/features/interviews/hooks/use-interview-runtime";
import { useInterviewSession } from "@/features/interviews/hooks/use-interview-sessions";
import { EvaluationSessionResults } from "@/features/evaluations/components/evaluation-session-results";
import { SpeechSessionResults } from "@/features/speech/components/speech-session-results";

interface InterviewResultsPageProps {
  sessionId: string;
}

export function InterviewResultsPage({ sessionId }: InterviewResultsPageProps) {
  const { data: session, isLoading: sessionLoading } = useInterviewSession(sessionId);
  const { data: runtime, isLoading: runtimeLoading } = useInterviewRuntime(sessionId);

  if (sessionLoading || runtimeLoading) {
    return (
      <div className="space-y-6 p-4 md:p-8">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-40 w-full rounded-xl" />
      </div>
    );
  }

  const answeredCount =
    runtime?.questions.filter(
      (q) => q.answer?.answer_text?.trim() || q.answer?.audio_storage_path,
    ).length ?? 0;
  const total = runtime?.questions.length ?? 0;

  return (
    <div className="mx-auto max-w-5xl space-y-8 p-4 md:p-8">
      <div className="space-y-3">
        <Link
          href={`/dashboard/interviews/${sessionId}`}
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to interview
        </Link>
        <div className="glass-card rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-6">
          <div className="flex flex-wrap items-start gap-4">
            <Trophy className="h-10 w-10 text-emerald-400" />
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Interview results</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                {session?.title ?? "Mock interview"} · {session?.target_role}
              </p>
              <p className="mt-2 text-sm">
                You answered <span className="font-medium text-foreground">{answeredCount}</span> of{" "}
                <span className="font-medium text-foreground">{total}</span> questions.
              </p>
            </div>
            <Button asChild variant="outline" className="ml-auto">
              <Link href="/dashboard/interviews">All interviews</Link>
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-8">
        <section className="glass-card rounded-2xl border border-border/60 p-6 md:p-8">
          <h2 className="mb-6 text-lg font-semibold tracking-tight">Communication & delivery</h2>
          <p className="mb-6 text-sm text-muted-foreground">
            How you sounded: pace, fillers, fluency, and confidence (used in answer scoring).
          </p>
          <SpeechSessionResults sessionId={sessionId} />
        </section>

        <section className="glass-card rounded-2xl border border-border/60 p-6 md:p-8">
          <h2 className="mb-6 text-lg font-semibold tracking-tight">Answer quality & marks</h2>
          <p className="mb-6 text-sm text-muted-foreground">
            Correct vs incorrect against expected answer points, session marks, and model answers.
          </p>
          <EvaluationSessionResults sessionId={sessionId} />
        </section>
      </div>
    </div>
  );
}
