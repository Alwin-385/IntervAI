import { apiClient } from "@/lib/api-client";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";
import type { WeakAreasAnalytics } from "@/features/weak-areas/types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

export async function fetchWeakAreasAnalytics(auth: Auth): Promise<WeakAreasAnalytics> {
  return apiClient<WeakAreasAnalytics>("/api/v1/analytics/weak-areas", auth);
}
