"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import {
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Loader2,
  Save,
  Flag,
  Send,
  Timer,
  Trophy,
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import type { InterviewSessionStateResponse } from "@/features/interviews/types";
import { VoiceRecorder } from "@/features/speech/components/voice-recorder";
import { FinishInterviewDialog } from "@/features/interviews/components/finish-interview-dialog";
import {
  useCompleteInterview,
  useSubmitInterviewAnswer,
} from "@/features/interviews/hooks/use-interview-runtime";

interface InterviewSessionPlayerProps {
  sessionId: string;
  runtime: InterviewSessionStateResponse;
}

const AUTOSAVE_MS = 10_000;

function hasAnswerContent(
  answer: { answer_text?: string | null; audio_storage_path?: string | null } | null | undefined,
) {
  if (!answer) return false;
  return Boolean(answer.answer_text?.trim()) || Boolean(answer.audio_storage_path);
}

function clampIndex(index: number, total: number) {
  return Math.max(0, Math.min(index, Math.max(total - 1, 0)));
}

function initialActiveIndex(runtime: InterviewSessionStateResponse) {
  const saved = runtime.progress.current_question_index;
  const withAnswers = runtime.questions.findIndex((q) => hasAnswerContent(q.answer));
  const candidate = saved > 0 ? saved : withAnswers >= 0 ? withAnswers : 0;
  return clampIndex(candidate, runtime.questions.length);
}

/** Questions submitted via "Submit & next" (not draft-only). */
function initialSubmittedIndices(runtime: InterviewSessionStateResponse): Set<number> {
  const submitted = new Set<number>();
  const cursor = runtime.progress.current_question_index;
  runtime.questions.forEach((q, idx) => {
    if (idx < cursor && hasAnswerContent(q.answer)) {
      submitted.add(idx);
    }
  });
  return submitted;
}

export function InterviewSessionPlayer({ sessionId, runtime }: InterviewSessionPlayerProps) {
  const router = useRouter();
  const total = runtime.questions.length;
  const totalDurationSeconds =
    runtime.total_duration_seconds ?? total * (runtime.seconds_per_question ?? 120);

  const [activeIndex, setActiveIndex] = useState(() => initialActiveIndex(runtime));
  const [submittedIndices, setSubmittedIndices] = useState<Set<number>>(() =>
    initialSubmittedIndices(runtime),
  );
  const [text, setText] = useState("");
  const [audioStoragePath, setAudioStoragePath] = useState<string | null>(null);
  const [answerDuration, setAnswerDuration] = useState<number | undefined>(undefined);
  const [questionStartedAt, setQuestionStartedAt] = useState(() => Date.now());
  const isVoiceMode = runtime.answer_mode === "voice";
  const [interviewRemaining, setInterviewRemaining] = useState(totalDurationSeconds);
  const [timeExpired, setTimeExpired] = useState(false);
  const [finishDialogOpen, setFinishDialogOpen] = useState(false);
  const textRef = useRef(text);
  const audioPathRef = useRef<string | null>(null);
  const answerDurationRef = useRef<number | undefined>(undefined);
  const autosaveRef = useRef<number | null>(null);
  const activeIndexRef = useRef(activeIndex);
  const savingRef = useRef(false);

  textRef.current = text;
  audioPathRef.current = audioStoragePath;
  answerDurationRef.current = answerDuration;
  activeIndexRef.current = activeIndex;

  const submit = useSubmitInterviewAnswer(sessionId);
  const complete = useCompleteInterview(sessionId);

  const active = runtime.questions[clampIndex(activeIndex, total)];
  const isFirst = activeIndex <= 0;
  const isLast = activeIndex >= total - 1;

  const answeredCount = useMemo(
    () => runtime.questions.filter((q) => hasAnswerContent(q.answer)).length,
    [runtime.questions],
  );

  const progressPercent = useMemo(() => {
    if (!total) return 0;
    return Math.round((answeredCount / total) * 100);
  }, [answeredCount, total]);

  const interviewStartedAt = useMemo(() => {
    if (runtime.started_at) return new Date(runtime.started_at).getTime();
    return Date.now();
  }, [runtime.started_at]);

  const saveCurrentAnswer = useCallback(
    async (opts: {
      autosave: boolean;
      advance: boolean;
      resumeIndex?: number;
    }) => {
      const idx = activeIndexRef.current;
      const item = runtime.questions[clampIndex(idx, total)];
      if (!item || savingRef.current) return;

      savingRef.current = true;
      try {
        return await submit.mutateAsync({
          question_id: item.question.id,
          answer_text: textRef.current,
          audio_storage_path: audioPathRef.current,
          duration_seconds: answerDurationRef.current ?? undefined,
          autosave: opts.autosave,
          advance: opts.advance,
          resume_question_index: opts.resumeIndex,
        });
      } finally {
        savingRef.current = false;
      }
    },
    [questionStartedAt, runtime.questions, submit, total],
  );

  const goToIndex = useCallback(
    async (nextIndex: number) => {
      const target = clampIndex(nextIndex, total);
      if (target === activeIndexRef.current) return;

      if (autosaveRef.current) {
        window.clearTimeout(autosaveRef.current);
        autosaveRef.current = null;
      }

      await saveCurrentAnswer({
        autosave: true,
        advance: false,
        resumeIndex: target,
      });

      setActiveIndex(target);
      setQuestionStartedAt(Date.now());
    },
    [saveCurrentAnswer, total],
  );

  useEffect(() => {
    if (!active) return;
    const serverText = active.answer?.answer_text ?? "";
    setText((prev) => {
      if (prev.trim().length > serverText.trim().length) return prev;
      return serverText;
    });
    setAudioStoragePath(active.answer?.audio_storage_path ?? null);
    setAnswerDuration(active.answer?.duration_seconds ?? undefined);
    setQuestionStartedAt(Date.now());
  }, [active?.question.id, active?.answer?.answer_text, active?.answer?.audio_storage_path]);

  useEffect(() => {
    const tick = () => {
      const elapsed = Math.floor((Date.now() - interviewStartedAt) / 1000);
      const remaining = Math.max(0, totalDurationSeconds - elapsed);
      setInterviewRemaining(remaining);
      if (remaining <= 0 && !timeExpired) {
        setTimeExpired(true);
        toast.warning("Interview time is up. Finish your current answer and submit.");
      }
    };
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [interviewStartedAt, totalDurationSeconds, timeExpired]);

  useEffect(() => {
    if (!active) return;
    if (autosaveRef.current) window.clearTimeout(autosaveRef.current);

    autosaveRef.current = window.setTimeout(() => {
      void saveCurrentAnswer({
        autosave: true,
        advance: false,
        resumeIndex: activeIndexRef.current,
      });
    }, AUTOSAVE_MS);

    return () => {
      if (autosaveRef.current) window.clearTimeout(autosaveRef.current);
    };
  }, [active?.question.id, text, saveCurrentAnswer]);

  if (!active) return null;

  const saveDraft = async () => {
    if (autosaveRef.current) {
      window.clearTimeout(autosaveRef.current);
      autosaveRef.current = null;
    }
    await saveCurrentAnswer({
      autosave: true,
      advance: false,
      resumeIndex: activeIndex,
    });
    toast.success("Draft saved");
  };

  const submitAndNext = async () => {
    if (autosaveRef.current) {
      window.clearTimeout(autosaveRef.current);
      autosaveRef.current = null;
    }

    const nextIndex = isLast ? activeIndex : activeIndex + 1;

    await saveCurrentAnswer({
      autosave: false,
      advance: !isLast,
      resumeIndex: isLast ? activeIndex : nextIndex,
    });

    if (isLast) {
      const result = await complete.mutateAsync();
      toast.success(`Interview completed in ${formatDuration(result.total_time_seconds)}`);
      router.push(`/dashboard/interviews/${sessionId}/results`);
      return;
    }

    setSubmittedIndices((prev) => new Set(prev).add(activeIndex));
    setActiveIndex(nextIndex);
    const nextItem = runtime.questions[nextIndex];
    setText(nextItem?.answer?.answer_text ?? "");
    setAudioStoragePath(nextItem?.answer?.audio_storage_path ?? null);
    setAnswerDuration(nextItem?.answer?.duration_seconds ?? undefined);
    setQuestionStartedAt(Date.now());
  };

  const finishInterviewEarly = async () => {
    if (autosaveRef.current) {
      window.clearTimeout(autosaveRef.current);
      autosaveRef.current = null;
    }
    await saveCurrentAnswer({
      autosave: true,
      advance: false,
      resumeIndex: activeIndex,
    });
    const result = await complete.mutateAsync();
    setFinishDialogOpen(false);
    toast.success(`Interview completed in ${formatDuration(result.total_time_seconds)}`);
    router.push(`/dashboard/interviews/${sessionId}/results`);
  };

  const autosaving = submit.isPending;

  if (runtime.status === "completed") {
    return (
      <div className="mx-auto flex min-h-[70vh] max-w-3xl flex-col items-center justify-center px-6 text-center">
        <div className="glass-card w-full rounded-3xl border border-emerald-500/30 bg-emerald-500/5 p-8">
          <Trophy className="mx-auto h-14 w-14 text-emerald-400" />
          <h2 className="mt-4 text-2xl font-bold">Interview complete</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            You answered {answeredCount} of {total} questions.
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            Completed at {new Date(runtime.completed_at ?? "").toLocaleString()}
          </p>
          <Button asChild className="mt-6 gap-2" size="lg">
            <Link href={`/dashboard/interviews/${sessionId}/results`}>
              View speech & communication results
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-[calc(100vh-5rem)] w-full max-w-4xl flex-col px-4 py-6 md:px-8">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wider text-muted-foreground">{runtime.title}</p>
          <h1 className="text-lg font-semibold">{runtime.target_role} mock interview</h1>
          <p className="mt-1 text-xs text-muted-foreground">
            {runtime.seconds_per_question / 60} min per question · {total} questions ·{" "}
            {Math.round(totalDurationSeconds / 60)} min total
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div
            className={cn(
              "flex items-center gap-3 rounded-full border px-4 py-2 text-sm",
              timeExpired
                ? "border-amber-500/50 bg-amber-500/10 text-amber-400"
                : "border-border/60 bg-background/70",
            )}
          >
            <Clock3 className="h-4 w-4 text-primary" />
            <span>
              Q {activeIndex + 1}/{total}
            </span>
            <span className="inline-flex items-center gap-1 font-medium">
              <Timer className="h-4 w-4 text-primary" />
              {formatTimer(interviewRemaining)}
            </span>
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="gap-1.5"
            onClick={() => setFinishDialogOpen(true)}
            disabled={submit.isPending || complete.isPending}
          >
            <Flag className="h-4 w-4" />
            Finish
          </Button>
        </div>
      </div>

      <div className="mb-4 space-y-2">
        <div className="flex flex-wrap gap-2">
          {runtime.questions.map((item, idx) => {
            const hasDraft = hasAnswerContent(item.answer);
            const isSubmitted = submittedIndices.has(idx);
            const isDraftOnly = hasDraft && !isSubmitted;
            const isActive = idx === activeIndex;
            return (
              <button
                key={item.question.id}
                type="button"
                disabled={submit.isPending}
                onClick={() => void goToIndex(idx)}
                className={cn(
                  "flex h-9 w-9 items-center justify-center rounded-lg border text-xs font-semibold transition-colors",
                  isActive && "border-primary bg-primary text-primary-foreground shadow-sm",
                  !isActive &&
                    isSubmitted &&
                    "border-emerald-500/50 bg-emerald-500/15 text-emerald-400",
                  !isActive &&
                    isDraftOnly &&
                    "border-amber-500/50 bg-amber-500/15 text-amber-400 ring-1 ring-amber-500/20",
                  !isActive &&
                    !hasDraft &&
                    !isSubmitted &&
                    "border-border/60 bg-muted/30 text-muted-foreground hover:border-primary/40 hover:bg-muted/50",
                )}
                aria-label={
                  isDraftOnly
                    ? `Question ${idx + 1}, draft saved`
                    : isSubmitted
                      ? `Question ${idx + 1}, submitted`
                      : `Question ${idx + 1}`
                }
                title={
                  isDraftOnly
                    ? "Draft saved"
                    : isSubmitted
                      ? "Submitted"
                      : undefined
                }
                aria-current={isActive ? "step" : undefined}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>
        <p className="text-[11px] text-muted-foreground">
          Click any question number to jump freely between questions.
        </p>
        <div className="flex flex-wrap items-center gap-4 text-[11px] text-muted-foreground">
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm border border-amber-500/50 bg-amber-500/15" />
            Draft saved
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm border border-emerald-500/50 bg-emerald-500/15" />
            Submitted
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm border border-primary bg-primary" />
            Current
          </span>
        </div>
      </div>

      <div className="mb-6 space-y-2">
        <Progress value={progressPercent} max={100} className="h-2.5" />
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{answeredCount} answered</span>
          <span>{progressPercent}% complete</span>
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={active.question.id}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.22 }}
          className="glass-card flex-1 rounded-3xl border border-border/60 p-5 md:p-8"
        >
          <div className="mb-4 flex items-start justify-between gap-3">
            <h2 className="text-xl font-semibold leading-snug">{active.question.question_text}</h2>
            <span className="shrink-0 text-xs uppercase tracking-wide text-muted-foreground">
              {active.question.category}
            </span>
          </div>

          {isVoiceMode ? (
            <VoiceRecorder
              sessionId={sessionId}
              questionId={active.question.id}
              transcript={text}
              audioStoragePath={audioStoragePath}
              onTranscriptChange={setText}
              onAudioStoragePathChange={setAudioStoragePath}
              onDurationChange={setAnswerDuration}
              disabled={submit.isPending || complete.isPending}
            />
          ) : (
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type your answer here..."
              className="h-64 w-full resize-none rounded-xl border border-input bg-background/70 p-4 text-sm outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring"
            />
          )}

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <div className="text-xs text-muted-foreground">
              {autosaving ? (
                <span className="inline-flex items-center gap-1">
                  <Loader2 className="h-3 w-3 animate-spin" /> Saving...
                </span>
              ) : (
                <span className="inline-flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3 text-emerald-400" /> Autosave every 10s
                </span>
              )}
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="outline"
                onClick={() => void goToIndex(activeIndex - 1)}
                disabled={isFirst || submit.isPending}
              >
                <ChevronLeft className="mr-1 h-4 w-4" />
                Previous
              </Button>
              <Button variant="outline" onClick={saveDraft} disabled={submit.isPending}>
                <Save className="mr-1 h-4 w-4" />
                Save draft
              </Button>
              {!isLast && (
                <Button
                  variant="outline"
                  onClick={() => void goToIndex(activeIndex + 1)}
                  disabled={submit.isPending}
                >
                  Next
                  <ChevronRight className="ml-1 h-4 w-4" />
                </Button>
              )}
              <Button onClick={submitAndNext} disabled={submit.isPending || complete.isPending}>
                <Send className="mr-1 h-4 w-4" />
                {isLast ? "Submit & finish" : "Submit & next"}
              </Button>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      <FinishInterviewDialog
        open={finishDialogOpen}
        onClose={() => setFinishDialogOpen(false)}
        onConfirm={() => void finishInterviewEarly()}
        isPending={complete.isPending || submit.isPending}
        answeredCount={answeredCount}
        totalQuestions={total}
      />
    </div>
  );
}

function formatTimer(seconds: number): string {
  const m = Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function formatDuration(total: number | null): string {
  if (!total) return "a short time";
  const mins = Math.round(total / 60);
  if (mins < 1) return `${Math.round(total)}s`;
  return `${mins} min`;
}
