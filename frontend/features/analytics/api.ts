import { apiClient } from "@/lib/api-client";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";
import type {
  AnalyticsDashboard,
  AnalyticsDashboardParams,
  AnalyticsProgress,
} from "@/features/analytics/types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

/** Backend accepts 7–365; default 90 keeps Render free tier responsive. */
function resolveDays(days: number | undefined): string {
  return String(days ?? 90);
}

function authOpts(auth: Auth) {
  return { getToken: auth.getToken, refreshToken: auth.refreshToken, token: auth.token };
}

export async function fetchAnalyticsDashboard(
  auth: Auth,
  params: AnalyticsDashboardParams = {},
): Promise<AnalyticsDashboard> {
  return apiClient<AnalyticsDashboard>("/api/v1/analytics/dashboard", {
    ...authOpts(auth),
    timeoutMs: 60_000,
    networkRetries: 1,
    params: {
      page: String(params.page ?? 1),
      page_size: String(params.page_size ?? 10),
      days: resolveDays(params.days),
      ...(params.target_role ? { target_role: params.target_role } : {}),
      ...(params.category ? { category: params.category } : {}),
    },
  });
}

export async function fetchAnalyticsProgress(
  auth: Auth,
  params: Omit<AnalyticsDashboardParams, "page" | "page_size"> = {},
): Promise<AnalyticsProgress> {
  return apiClient<AnalyticsProgress>("/api/v1/analytics/progress", {
    ...authOpts(auth),
    timeoutMs: 60_000,
    networkRetries: 1,
    params: {
      days: resolveDays(params.days),
      ...(params.target_role ? { target_role: params.target_role } : {}),
      ...(params.category ? { category: params.category } : {}),
    },
  });
}
