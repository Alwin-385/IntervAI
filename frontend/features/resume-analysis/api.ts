import { apiClient, ApiError } from "@/lib/api-client";
import type { ResumeAnalysisDetail, ResumeAnalyzeRequest } from "@/features/resume-analysis/types";

export async function startResumeAnalysis(
  token: string,
  resumeId: string,
  body?: ResumeAnalyzeRequest,
): Promise<ResumeAnalysisDetail> {
  return apiClient<ResumeAnalysisDetail>(`/api/v1/resumes/${resumeId}/analyze`, {
    method: "POST",
    token,
    body: JSON.stringify(body ?? {}),
  });
}

export async function fetchResumeAnalysis(
  token: string,
  resumeId: string,
): Promise<ResumeAnalysisDetail | null> {
  try {
    return await apiClient<ResumeAnalysisDetail>(`/api/v1/resumes/${resumeId}/analysis`, {
      token,
      params: { _t: String(Date.now()) },
    });
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}
