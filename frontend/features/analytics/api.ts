import { apiClient } from "@/lib/api-client";
import { ensureBackendAwake } from "@/lib/backend-health";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";
import type {
  AnalyticsDashboard,
  AnalyticsDashboardParams,
  AnalyticsProgress,
} from "@/features/analytics/types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

/** Backend accepts 7–365; default 30 matches fast historical behavior. */
function resolveDays(days: number | undefined): string {
  return String(days ?? 30);
}

function authOpts(auth: Auth) {
  return { getToken: auth.getToken, refreshToken: auth.refreshToken, token: auth.token };
}

export async function fetchAnalyticsDashboard(
  auth: Auth,
  params: AnalyticsDashboardParams = {},
): Promise<AnalyticsDashboard> {
  await ensureBackendAwake();
  return apiClient<AnalyticsDashboard>("/api/v1/analytics/dashboard", {
    ...authOpts(auth),
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
  await ensureBackendAwake();
  return apiClient<AnalyticsProgress>("/api/v1/analytics/progress", {
    ...authOpts(auth),
    params: {
      days: resolveDays(params.days),
      ...(params.target_role ? { target_role: params.target_role } : {}),
      ...(params.category ? { category: params.category } : {}),
    },
  });
}
