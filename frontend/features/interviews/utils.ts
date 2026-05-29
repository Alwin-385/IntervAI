import {
  ANSWER_MODES,
  CATEGORIES,
  DIFFICULTIES,
} from "@/features/interviews/constants";
import type {
  AnswerMode,
  InterviewCategory,
  InterviewDifficulty,
  InterviewSessionStatus,
} from "@/features/interviews/types";

export function categoryLabel(value: InterviewCategory): string {
  return CATEGORIES.find((c) => c.value === value)?.label ?? value;
}

export function difficultyLabel(value: InterviewDifficulty): string {
  return DIFFICULTIES.find((d) => d.value === value)?.label ?? value;
}

export function answerModeLabel(value: AnswerMode): string {
  return ANSWER_MODES.find((a) => a.value === value)?.label ?? value;
}

export function statusLabel(status: InterviewSessionStatus): string {
  switch (status) {
    case "scheduled":
      return "Scheduled";
    case "in_progress":
      return "In progress";
    case "completed":
      return "Completed";
    case "cancelled":
      return "Cancelled";
    default:
      return status;
  }
}

export function formatTimeLimit(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const m = Math.round(seconds / 60);
  return m === 1 ? "1 min" : `${m} min`;
}

export function statusTone(status: InterviewSessionStatus): string {
  switch (status) {
    case "scheduled":
      return "bg-primary/15 text-primary";
    case "in_progress":
      return "bg-amber-500/15 text-amber-400";
    case "completed":
      return "bg-emerald-500/15 text-emerald-400";
    case "cancelled":
      return "bg-muted text-muted-foreground";
    default:
      return "bg-muted text-muted-foreground";
  }
}
