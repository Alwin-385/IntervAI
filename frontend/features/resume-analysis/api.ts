import { apiClient, ApiError } from "@/lib/api-client";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";
import type { ResumeAnalysisDetail, ResumeAnalyzeRequest } from "@/features/resume-analysis/types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

export async function startResumeAnalysis(
  auth: Auth,
  resumeId: string,
  body?: ResumeAnalyzeRequest,
): Promise<ResumeAnalysisDetail> {
  return apiClient<ResumeAnalysisDetail>(`/api/v1/resumes/${resumeId}/analyze`, {
    method: "POST",
    body: JSON.stringify(body ?? {}),
    ...auth,
  });
}

export async function fetchResumeAnalysis(
  auth: Auth,
  resumeId: string,
): Promise<ResumeAnalysisDetail | null> {
  try {
    return await apiClient<ResumeAnalysisDetail>(`/api/v1/resumes/${resumeId}/analysis`, {
      ...auth,
      params: { _t: String(Date.now()) },
    });
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}
