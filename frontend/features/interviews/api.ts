import { apiClient } from "@/lib/api-client";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";
import type {
  CompleteInterviewResponse,
  GenerateQuestionsResponse,
  InterviewCreateRequest,
  InterviewQuestionDetail,
  InterviewSessionStateResponse,
  InterviewSetupResponse,
  SubmitAnswerRequest,
  SubmitAnswerResponse,
} from "@/features/interviews/types";

export type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

export async function createInterview(
  auth: Auth,
  body: InterviewCreateRequest,
): Promise<InterviewSetupResponse> {
  return apiClient<InterviewSetupResponse>("/api/v1/interviews/create", {
    method: "POST",
    body: JSON.stringify(body),
    ...auth,
  });
}

export async function generateInterviewQuestions(
  auth: Auth,
  sessionId: string,
  replaceExisting = true,
): Promise<GenerateQuestionsResponse> {
  return apiClient<GenerateQuestionsResponse>(
    `/api/v1/interviews/${sessionId}/generate-questions`,
    {
      method: "POST",
      params: { replace_existing: String(replaceExisting) },
      timeoutMs: 120_000,
      ...auth,
    },
  );
}

export async function fetchInterviewQuestions(
  auth: Auth,
  sessionId: string,
): Promise<InterviewQuestionDetail[]> {
  return apiClient<InterviewQuestionDetail[]>(`/api/v1/interviews/${sessionId}/questions`, auth);
}

export async function deleteInterview(
  auth: Auth,
  sessionId: string,
): Promise<{ message: string }> {
  return apiClient<{ message: string }>(`/api/v1/interviews/${sessionId}`, {
    method: "DELETE",
    ...auth,
  });
}

export async function fetchInterviewSessionState(
  auth: Auth,
  sessionId: string,
): Promise<InterviewSessionStateResponse> {
  return apiClient<InterviewSessionStateResponse>(`/api/v1/interviews/${sessionId}/state`, auth);
}

export async function submitInterviewAnswer(
  auth: Auth,
  sessionId: string,
  body: SubmitAnswerRequest,
): Promise<SubmitAnswerResponse> {
  return apiClient<SubmitAnswerResponse>(`/api/v1/interviews/${sessionId}/submit-answer`, {
    method: "POST",
    body: JSON.stringify(body),
    ...auth,
  });
}

export async function completeInterviewSession(
  auth: Auth,
  sessionId: string,
): Promise<CompleteInterviewResponse> {
  return apiClient<CompleteInterviewResponse>(`/api/v1/interviews/${sessionId}/complete`, {
    method: "POST",
    ...auth,
  });
}
