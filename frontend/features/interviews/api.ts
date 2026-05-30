import { apiClient } from "@/lib/api-client";
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

export async function createInterview(
  token: string,
  body: InterviewCreateRequest,
): Promise<InterviewSetupResponse> {
  return apiClient<InterviewSetupResponse>("/api/v1/interviews/create", {
    method: "POST",
    token,
    body: JSON.stringify(body),
  });
}

export async function generateInterviewQuestions(
  token: string,
  sessionId: string,
  replaceExisting = true,
): Promise<GenerateQuestionsResponse> {
  return apiClient<GenerateQuestionsResponse>(
    `/api/v1/interviews/${sessionId}/generate-questions`,
    {
      method: "POST",
      token,
      params: { replace_existing: String(replaceExisting) },
      timeoutMs: 120_000,
    },
  );
}

export async function fetchInterviewQuestions(
  token: string,
  sessionId: string,
): Promise<InterviewQuestionDetail[]> {
  return apiClient<InterviewQuestionDetail[]>(`/api/v1/interviews/${sessionId}/questions`, {
    token,
  });
}

export async function deleteInterview(
  token: string,
  sessionId: string,
): Promise<{ message: string }> {
  return apiClient<{ message: string }>(`/api/v1/interviews/${sessionId}`, {
    method: "DELETE",
    token,
  });
}

export async function fetchInterviewSessionState(
  token: string,
  sessionId: string,
): Promise<InterviewSessionStateResponse> {
  return apiClient<InterviewSessionStateResponse>(`/api/v1/interviews/${sessionId}/state`, {
    token,
  });
}

export async function submitInterviewAnswer(
  token: string,
  sessionId: string,
  body: SubmitAnswerRequest,
): Promise<SubmitAnswerResponse> {
  return apiClient<SubmitAnswerResponse>(`/api/v1/interviews/${sessionId}/submit-answer`, {
    method: "POST",
    token,
    body: JSON.stringify(body),
  });
}

export async function completeInterviewSession(
  token: string,
  sessionId: string,
): Promise<CompleteInterviewResponse> {
  return apiClient<CompleteInterviewResponse>(`/api/v1/interviews/${sessionId}/complete`, {
    method: "POST",
    token,
  });
}
