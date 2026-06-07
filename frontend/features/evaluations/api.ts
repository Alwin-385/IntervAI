import { apiClient } from "@/lib/api-client";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";
import type {
  AnswerEvaluationDetail,
  SessionAnswerEvaluationResults,
} from "@/features/evaluations/types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

function authOpts(auth: Auth) {
  return {
    getToken: auth.getToken,
    refreshToken: auth.refreshToken,
    token: auth.token,
  };
}

export async function evaluateAnswer(
  auth: Auth,
  answerId: string,
  force = false,
): Promise<AnswerEvaluationDetail> {
  return apiClient<AnswerEvaluationDetail>(`/api/v1/answers/${answerId}/evaluate`, {
    method: "POST",
    body: JSON.stringify({ force }),
    ...authOpts(auth),
  });
}

export async function fetchAnswerEvaluation(
  auth: Auth,
  answerId: string,
): Promise<AnswerEvaluationDetail> {
  return apiClient<AnswerEvaluationDetail>(`/api/v1/answers/${answerId}/evaluation`, {
    ...authOpts(auth),
  });
}

export async function fetchSessionAnswerEvaluations(
  auth: Auth,
  sessionId: string,
): Promise<SessionAnswerEvaluationResults> {
  return apiClient<SessionAnswerEvaluationResults>(
    `/api/v1/answers/session/${sessionId}/evaluation`,
    { ...authOpts(auth) },
  );
}

/** @deprecated pass auth object with getToken instead */
export async function fetchSessionAnswerEvaluationsWithToken(
  token: string,
  sessionId: string,
  refreshToken?: TokenRefresh,
): Promise<SessionAnswerEvaluationResults> {
  return fetchSessionAnswerEvaluations({ token, refreshToken }, sessionId);
}
