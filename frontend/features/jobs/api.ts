import { apiClient } from "@/lib/api-client";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";
import type { BackgroundJob } from "@/features/jobs/types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

export async function fetchJob(auth: Auth, jobId: string): Promise<BackgroundJob> {
  return apiClient<BackgroundJob>(`/api/v1/jobs/${jobId}`, auth);
}

export async function fetchJobsForResource(
  auth: Auth,
  resourceType: string,
  resourceId: string,
): Promise<{ items: BackgroundJob[]; total: number }> {
  return apiClient<{ items: BackgroundJob[]; total: number }>("/api/v1/jobs", {
    ...auth,
    params: { resource_type: resourceType, resource_id: resourceId },
  });
}
