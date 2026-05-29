import { apiClient } from "@/lib/api-client";

import { normalizeResume, normalizeResumeList } from "./utils";
import type {
  PaginatedResumes,
  Resume,
  ResumeExtractionStatus,
  ResumeUploadResponse,
} from "./types";

export async function fetchResumes(
  token: string,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResumes> {
  const data = await apiClient<PaginatedResumes>("/api/v1/resumes", {
    token,
    params: { page: String(page), page_size: String(pageSize) },
  });
  return normalizeResumeList(data);
}

export async function fetchResume(
  token: string,
  resumeId: string,
): Promise<Resume> {
  const resume = await apiClient<Resume>(`/api/v1/resumes/${resumeId}`, { token });
  return normalizeResume(resume);
}

export async function fetchExtractionStatus(
  token: string,
  resumeId: string,
): Promise<ResumeExtractionStatus> {
  return apiClient<ResumeExtractionStatus>(`/api/v1/resumes/${resumeId}/extraction`, {
    token,
  });
}

export async function retryExtraction(
  token: string,
  resumeId: string,
): Promise<ResumeExtractionStatus> {
  return apiClient<ResumeExtractionStatus>(
    `/api/v1/resumes/${resumeId}/extraction/retry`,
    { method: "POST", token },
  );
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export type { ResumeUploadResponse };
