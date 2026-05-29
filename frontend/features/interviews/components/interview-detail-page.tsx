"use client";

import Link from "next/link";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  Briefcase,
  FileText,
  Hash,
  Layers,
  Loader2,
  Mic,
  Pencil,
  RefreshCw,
  Sparkles,
  Target,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { DeleteInterviewDialog } from "@/features/interviews/components/delete-interview-dialog";
import { QuestionCard } from "@/features/interviews/components/question-card";
import { useGenerateQuestions } from "@/features/interviews/hooks/use-generate-questions";
import { useInterviewQuestions } from "@/features/interviews/hooks/use-interview-questions";
import { useInterviewSession } from "@/features/interviews/hooks/use-interview-sessions";
import {
  answerModeLabel,
  categoryLabel,
  difficultyLabel,
  statusLabel,
  statusTone,
} from "@/features/interviews/utils";

interface InterviewDetailPageProps {
  sessionId: string;
}

export function InterviewDetailPage({ sessionId }: InterviewDetailPageProps) {
  const { data: session, isLoading: sessionLoading } = useInterviewSession(sessionId);
  const { data: questions, isLoading: questionsLoading, refetch } =
    useInterviewQuestions(sessionId);
  const generate = useGenerateQuestions(sessionId);

  const handleGenerate = () => {
    generate.mutate(true, {
      onSuccess: (data) => {
        const planned = session?.question_count ?? data.count;
        if (data.count < planned) {
          toast.warning(`Generated ${data.count} of ${planned} questions`);
        } else {
          toast.success(`Generated ${data.count} personalized questions`);
        }
        void refetch();
      },
      onError: (err) =>
        toast.error(err instanceof Error ? err.message : "Failed to generate questions"),
    });
  };

  if (sessionLoading) {
    return (
      <div className="space-y-6 p-4 md:p-8">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-40 w-full rounded-xl" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="space-y-4 p-4 md:p-8">
        <Link
          href="/dashboard/interviews"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to interviews
        </Link>
        <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          Interview session not found.
        </p>
      </div>
    );
  }

  const questionCount = questions?.length ?? 0;
  const hasQuestions = questionCount > 0;
  const plannedCount = session.question_count;
  const meta: { icon: typeof Briefcase; label: string; value: string }[] = [
    { icon: Briefcase, label: "Target role", value: session.target_role },
    { icon: Layers, label: "Category", value: categoryLabel(session.category) },
    { icon: Target, label: "Difficulty", value: difficultyLabel(session.difficulty) },
    {
      icon: Hash,
      label: "Planned questions",
      value: hasQuestions ? `${questionCount} / ${plannedCount}` : `${plannedCount}`,
    },
    {
      icon: session.answer_mode === "voice" ? Mic : Pencil,
      label: "Answer mode",
      value: answerModeLabel(session.answer_mode),
    },
  ];
  if (session.resume_id) {
    meta.push({ icon: FileText, label: "Resume", value: "Linked for personalization" });
  }

  return (
    <div className="space-y-8 p-4 md:p-8">
      <div className="space-y-3">
        <Link
          href="/dashboard/interviews"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to interviews
        </Link>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 text-primary">
              <Sparkles className="h-5 w-5" />
              <span className="text-sm font-medium">Interview session</span>
            </div>
            <h1 className="mt-1 text-2xl font-bold tracking-tight">{session.title}</h1>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge className={statusTone(session.status)}>{statusLabel(session.status)}</Badge>
            <DeleteInterviewDialog
              sessionId={sessionId}
              sessionTitle={session.title}
            />
          </div>
        </div>
      </div>

      <div className="glass-card rounded-2xl border border-border/60 p-6">
        <ul className="grid gap-4 sm:grid-cols-2">
          {meta.map(({ icon: Icon, label, value }) => (
            <li key={label} className="flex items-center gap-3 text-sm">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Icon className="h-4 w-4" />
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {label}
                </p>
                <p className="text-sm font-medium text-foreground">{value}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Interview questions</h2>
          <p className="text-sm text-muted-foreground">
            {generate.isGenerating
              ? `Generating ${plannedCount} questions…`
              : hasQuestions
                ? `${questionCount} of ${plannedCount} personalized questions ready`
                : "Generate AI questions tailored to your role, resume, and weak areas"}
          </p>
        </div>
        <div className="flex gap-2">
          {hasQuestions && session.status !== "completed" && (
            <Button asChild variant="secondary" className="gap-2">
              <Link href={`/dashboard/interviews/${sessionId}/session`}>
                {session.status === "in_progress" ? "Resume interview" : "Start interview"}
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          )}
          {session.status === "completed" && (
            <Button asChild variant="secondary" className="gap-2">
              <Link href={`/dashboard/interviews/${sessionId}/results`}>
                Speech & results
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          )}
          <Button
            onClick={handleGenerate}
            disabled={generate.isGenerating}
            className="gap-2"
          >
            {generate.isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating…
              </>
            ) : hasQuestions ? (
              <>
                <RefreshCw className="h-4 w-4" />
                Regenerate
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Generate questions
              </>
            )}
          </Button>
        </div>
      </div>

      {(questionsLoading || generate.isGenerating) && (
        <div className="space-y-3">
          {Array.from({ length: plannedCount }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-2xl" />
          ))}
        </div>
      )}

      {!questionsLoading && !hasQuestions && !generate.isGenerating && (
        <div className="glass-card rounded-2xl border border-dashed border-primary/30 bg-primary/5 py-14 text-center">
          <Sparkles className="mx-auto mb-4 h-10 w-10 text-primary" />
          <p className="text-lg font-medium">No questions yet</p>
          <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
            We use your resume, target role, difficulty, and weak areas to build realistic
            interviewer-style questions — not generic repeats.
          </p>
          <Button onClick={handleGenerate} className="mt-6 gap-2">
            <Sparkles className="h-4 w-4" />
            Generate {session.question_count} questions
          </Button>
        </div>
      )}

      {generate.isGenerating && (
        <div className="glass-card flex items-center gap-3 rounded-2xl border border-primary/20 bg-primary/5 p-6">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
          <div>
            <p className="font-medium">
              Building your {plannedCount} question{plannedCount === 1 ? "" : "s"}…
            </p>
            <p className="text-sm text-muted-foreground">
              Personalizing to your role, resume, and difficulty — this usually takes a few
              seconds.
            </p>
          </div>
        </div>
      )}

      {!generate.isGenerating && !questionsLoading && hasQuestions && (
        <div className="space-y-4">
          {questions!.map((q, idx) => (
            <QuestionCard key={q.id} question={q} index={idx} />
          ))}
        </div>
      )}
    </div>
  );
}
