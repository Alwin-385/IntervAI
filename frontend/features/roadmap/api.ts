import { apiClient, ApiError } from "@/lib/api-client";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";
import type { GeneratedRoadmap } from "@/features/roadmap/types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

function authOpts(auth: Auth) {
  return { getToken: auth.getToken, refreshToken: auth.refreshToken, token: auth.token };
}

export async function generateRoadmap(
  auth: Auth,
  targetRole?: string,
): Promise<GeneratedRoadmap> {
  return apiClient<GeneratedRoadmap>("/api/v1/roadmap/generate", {
    method: "POST",
    body: JSON.stringify({ target_role: targetRole ?? null, force_regenerate: true }),
    ...authOpts(auth),
  });
}

export async function fetchRoadmap(
  auth: Auth,
  targetRole?: string,
): Promise<GeneratedRoadmap | null> {
  try {
    return await apiClient<GeneratedRoadmap>("/api/v1/roadmap", {
      ...authOpts(auth),
      params: targetRole ? { target_role: targetRole } : undefined,
    });
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

export async function updateRoadmapItem(
  auth: Auth,
  roadmapId: string,
  itemId: string,
  completed: boolean,
): Promise<GeneratedRoadmap> {
  return apiClient<GeneratedRoadmap>(`/api/v1/roadmap/${roadmapId}/items/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify({ completed }),
    ...authOpts(auth),
  });
}
