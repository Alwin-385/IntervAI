export type BackgroundJobStatus =
  | "pending"
  | "running"
  | "retrying"
  | "completed"
  | "failed"
  | "cancelled";

export type BackgroundJobType =
  | "resume_extraction"
  | "resume_analysis"
  | "question_generation"
  | "transcription"
  | "answer_evaluation"
  | "roadmap_generation";

export interface BackgroundJob {
  id: string;
  user_id: string;
  job_type: BackgroundJobType;
  status: BackgroundJobStatus;
  celery_task_id: string | null;
  resource_type: string | null;
  resource_id: string | null;
  progress_percent: number;
  progress_step: string | null;
  progress_message: string | null;
  result: Record<string, unknown> | null;
  error_message: string | null;
  retry_count: number;
  max_retries: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  is_terminal: boolean;
}

export const TERMINAL_JOB_STATUSES: BackgroundJobStatus[] = [
  "completed",
  "failed",
  "cancelled",
];
