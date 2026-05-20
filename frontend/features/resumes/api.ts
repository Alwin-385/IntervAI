import { apiClient } from "@/lib/api-client";

import type { PaginatedResumes, Resume, ResumeUploadResponse } from "./types";

export async function fetchResumes(
  token: string,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResumes> {
  return apiClient<PaginatedResumes>("/api/v1/resumes", {
    token,
    params: { page: String(page), page_size: String(pageSize) },
  });
}

export async function fetchResume(
  token: string,
  resumeId: string,
): Promise<Resume> {
  return apiClient<Resume>(`/api/v1/resumes/${resumeId}`, { token });
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export type { ResumeUploadResponse };
