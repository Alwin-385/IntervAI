import { getApiBaseUrl } from "@/lib/env";
import type {
  AnswerEvaluationDetail,
  SessionAnswerEvaluationResults,
} from "@/features/evaluations/types";

export class EvaluationApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: unknown,
  ) {
    super(message);
    this.name = "EvaluationApiError";
  }
}

export async function evaluateAnswer(
  token: string,
  answerId: string,
  force = false,
): Promise<AnswerEvaluationDetail> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/answers/${answerId}/evaluate`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ force }),
  });
  const body = await res.json();
  if (!res.ok) throw new EvaluationApiError(parseError(body), res.status, body);
  return body as AnswerEvaluationDetail;
}

export async function fetchAnswerEvaluation(
  token: string,
  answerId: string,
): Promise<AnswerEvaluationDetail> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/answers/${answerId}/evaluation`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  const body = await res.json();
  if (!res.ok) throw new EvaluationApiError(parseError(body), res.status, body);
  return body as AnswerEvaluationDetail;
}

export async function fetchSessionAnswerEvaluations(
  token: string,
  sessionId: string,
): Promise<SessionAnswerEvaluationResults> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/answers/session/${sessionId}/evaluation`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  const body = await res.json();
  if (!res.ok) throw new EvaluationApiError(parseError(body), res.status, body);
  return body as SessionAnswerEvaluationResults;
}

function parseError(body: unknown): string {
  if (
    typeof body === "object" &&
    body !== null &&
    "error" in body &&
    typeof (body as { error?: { message?: string } }).error?.message === "string"
  ) {
    return (body as { error: { message: string } }).error.message;
  }
  return "Answer evaluation request failed";
}
