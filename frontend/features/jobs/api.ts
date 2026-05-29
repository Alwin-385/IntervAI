import { getApiBaseUrl } from "@/lib/env";
import type { BackgroundJob } from "@/features/jobs/types";

async function handleResponse<T>(res: Response): Promise<T> {
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const msg =
      typeof body === "object" &&
      body !== null &&
      "error" in body &&
      typeof (body as { error?: { message?: string } }).error?.message === "string"
        ? (body as { error: { message: string } }).error.message
        : "Job request failed";
    throw new Error(msg);
  }
  return body as T;
}

export async function fetchJob(token: string, jobId: string): Promise<BackgroundJob> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/jobs/${jobId}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return handleResponse<BackgroundJob>(res);
}

export async function fetchJobsForResource(
  token: string,
  resourceType: string,
  resourceId: string,
): Promise<{ items: BackgroundJob[]; total: number }> {
  const q = new URLSearchParams({ resource_type: resourceType, resource_id: resourceId });
  const res = await fetch(`${getApiBaseUrl()}/api/v1/jobs?${q}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return handleResponse<{ items: BackgroundJob[]; total: number }>(res);
}
