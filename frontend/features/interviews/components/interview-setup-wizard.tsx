"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, ArrowRight, Loader2, Rocket, Sparkles, X } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { useCreateInterview } from "@/features/interviews/hooks/use-create-interview";
import { useResumes } from "@/features/resumes/hooks/use-resumes";
import { ResumePickerInline } from "@/features/interviews/components/resume-picker-inline";
import { StepAnswerMode } from "@/features/interviews/components/step-answer-mode";
import { StepCategory } from "@/features/interviews/components/step-category";
import { StepDifficulty } from "@/features/interviews/components/step-difficulty";
import { StepQuestionCount } from "@/features/interviews/components/step-question-count";
import { StepReview } from "@/features/interviews/components/step-review";
import { StepRole } from "@/features/interviews/components/step-role";
import { WizardProgress } from "@/features/interviews/components/wizard-progress";
import { STEP_LABELS } from "@/features/interviews/constants";
import {
  DEFAULT_WIZARD_STATE,
  type AnswerMode,
  type InterviewCategory,
  type InterviewDifficulty,
  type InterviewWizardState,
} from "@/features/interviews/types";

const TOTAL_STEPS = STEP_LABELS.length;

export function InterviewSetupWizard() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [state, setState] = useState<InterviewWizardState>(DEFAULT_WIZARD_STATE);
  const [direction, setDirection] = useState<1 | -1>(1);
  const createMutation = useCreateInterview();

  const { data: resumesData } = useResumes(1, 10);
  const selectedResume = useMemo(
    () => resumesData?.items.find((r) => r.id === state.resume_id) ?? null,
    [resumesData, state.resume_id],
  );

  const setRole = (role: string, custom: boolean) =>
    setState((s) => ({ ...s, target_role: role, custom_role: custom }));
  const setCategory = (category: InterviewCategory) =>
    setState((s) => ({
      ...s,
      category,
      resume_id: category === "resume_based" ? s.resume_id : null,
    }));
  const setDifficulty = (difficulty: InterviewDifficulty) =>
    setState((s) => ({ ...s, difficulty }));
  const setQuestionCount = (n: number) =>
    setState((s) => ({ ...s, question_count: n }));
  const setAnswerMode = (mode: AnswerMode) =>
    setState((s) => ({ ...s, answer_mode: mode }));
  const setResumeId = (resumeId: string | null) =>
    setState((s) => ({ ...s, resume_id: resumeId }));

  const validation = validateStep(step, state);

  const goNext = () => {
    if (!validation.ok) {
      toast.error(validation.message);
      return;
    }
    if (step < TOTAL_STEPS - 1) {
      setDirection(1);
      setStep((s) => s + 1);
    }
  };

  const goBack = () => {
    if (step === 0) {
      router.push("/dashboard/interviews");
      return;
    }
    setDirection(-1);
    setStep((s) => s - 1);
  };

  const goToStep = (target: number) => {
    if (target < 0 || target >= TOTAL_STEPS || target > step) return;
    setDirection(-1);
    setStep(target);
  };

  const handleSubmit = async () => {
    if (!validation.ok) {
      toast.error(validation.message);
      return;
    }
    if (!state.category || !state.difficulty || !state.answer_mode) return;

    try {
      const result = await createMutation.mutateAsync({
        target_role: state.target_role.trim(),
        category: state.category,
        difficulty: state.difficulty,
        answer_mode: state.answer_mode,
        question_count: state.question_count,
        resume_id: state.resume_id ?? undefined,
      });
      toast.success("Interview session created");
      router.push(`/dashboard/interviews/${result.id}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create interview");
    }
  };

  return (
    <div className="mx-auto w-full max-w-4xl space-y-6 p-4 md:p-8">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 text-primary">
            <Sparkles className="h-5 w-5" />
            <span className="text-sm font-medium">New interview</span>
          </div>
          <h1 className="mt-1 text-2xl font-bold tracking-tight">
            Set up your mock interview
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Six quick steps. Configure once — practice anytime.
          </p>
        </div>
        <Button variant="ghost" size="sm" asChild className="gap-1.5">
          <Link href="/dashboard/interviews">
            <X className="h-4 w-4" />
            Cancel
          </Link>
        </Button>
      </header>

      <WizardProgress currentStep={step} onStepClick={goToStep} />

      <div className="glass-card relative min-h-[420px] overflow-hidden rounded-2xl border border-border/60 p-6 md:p-8">
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={step}
            custom={direction}
            initial={{ opacity: 0, x: direction === 1 ? 28 : -28 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: direction === 1 ? -28 : 28 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
          >
            {step === 0 && (
              <StepRole
                value={state.target_role}
                custom={state.custom_role}
                onChange={setRole}
              />
            )}
            {step === 1 && (
              <div className="space-y-5">
                <StepCategory value={state.category} onChange={setCategory} />
                {state.category === "resume_based" && (
                  <ResumePickerInline
                    value={state.resume_id}
                    onChange={setResumeId}
                  />
                )}
              </div>
            )}
            {step === 2 && (
              <StepDifficulty value={state.difficulty} onChange={setDifficulty} />
            )}
            {step === 3 && (
              <StepQuestionCount
                value={state.question_count}
                onChange={setQuestionCount}
              />
            )}
            {step === 4 && (
              <StepAnswerMode value={state.answer_mode} onChange={setAnswerMode} />
            )}
            {step === 5 && (
              <StepReview
                state={state}
                resumeTitle={selectedResume?.title ?? selectedResume?.file_name ?? null}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="flex flex-col-reverse items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Button
          variant="outline"
          onClick={goBack}
          disabled={createMutation.isPending}
          className="gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          {step === 0 ? "Back to interviews" : "Back"}
        </Button>
        {step < TOTAL_STEPS - 1 ? (
          <Button onClick={goNext} className="gap-2" size="lg">
            Next
            <ArrowRight className="h-4 w-4" />
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            disabled={createMutation.isPending}
            className="gap-2"
            size="lg"
          >
            {createMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating…
              </>
            ) : (
              <>
                <Rocket className="h-4 w-4" />
                Create interview
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}

function validateStep(
  step: number,
  state: InterviewWizardState,
): { ok: boolean; message: string } {
  if (step === 0) {
    if (!state.target_role.trim()) {
      return { ok: false, message: "Pick or type a target role to continue" };
    }
  }
  if (step === 1) {
    if (!state.category) {
      return { ok: false, message: "Select an interview category" };
    }
    if (state.category === "resume_based" && !state.resume_id) {
      return {
        ok: false,
        message: "Pick a completed resume — or choose another category",
      };
    }
  }
  if (step === 2 && !state.difficulty) {
    return { ok: false, message: "Pick a difficulty level" };
  }
  if (step === 3) {
    if (
      !Number.isFinite(state.question_count) ||
      state.question_count < 3 ||
      state.question_count > 25
    ) {
      return { ok: false, message: "Question count must be between 3 and 25" };
    }
  }
  if (step === 4 && !state.answer_mode) {
    return { ok: false, message: "Pick an answer mode" };
  }
  if (step === 5) {
    if (
      !state.target_role.trim() ||
      !state.category ||
      !state.difficulty ||
      !state.answer_mode
    ) {
      return { ok: false, message: "Some choices are missing — go back to complete them" };
    }
  }
  return { ok: true, message: "" };
}
