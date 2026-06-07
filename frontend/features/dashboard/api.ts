import { apiClient } from "@/lib/api-client";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";
import type { DashboardOverview } from "@/features/dashboard/types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

export async function fetchDashboardOverview(auth: Auth): Promise<DashboardOverview> {
  return apiClient<DashboardOverview>("/api/v1/dashboard/overview", auth);
}
