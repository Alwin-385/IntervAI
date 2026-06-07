import { apiClient } from "@/lib/api-client";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";

import { normalizeResume, normalizeResumeList } from "./utils";
import type {
  PaginatedResumes,
  Resume,
  ResumeExtractionStatus,
  ResumeUploadResponse,
} from "./types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

export async function fetchResumes(
  auth: Auth,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResumes> {
  const data = await apiClient<PaginatedResumes>("/api/v1/resumes", {
    ...auth,
    params: { page: String(page), page_size: String(pageSize) },
  });
  return normalizeResumeList(data);
}

export async function fetchResume(auth: Auth, resumeId: string): Promise<Resume> {
  const resume = await apiClient<Resume>(`/api/v1/resumes/${resumeId}`, auth);
  return normalizeResume(resume);
}

export async function fetchExtractionStatus(
  auth: Auth,
  resumeId: string,
): Promise<ResumeExtractionStatus> {
  return apiClient<ResumeExtractionStatus>(`/api/v1/resumes/${resumeId}/extraction`, auth);
}

export async function retryExtraction(
  auth: Auth,
  resumeId: string,
): Promise<ResumeExtractionStatus> {
  return apiClient<ResumeExtractionStatus>(`/api/v1/resumes/${resumeId}/extraction/retry`, {
    method: "POST",
    ...auth,
  });
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export type { ResumeUploadResponse };
