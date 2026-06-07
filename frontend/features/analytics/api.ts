import { getApiBaseUrl } from "@/lib/env";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";
import type {
  AnalyticsDashboard,
  AnalyticsDashboardParams,
  AnalyticsProgress,
} from "@/features/analytics/types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

function buildParams(params: Record<string, string | undefined>): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") out[key] = value;
  }
  return out;
}

async function analyticsFetch<T>(
  auth: Auth,
  path: string,
  params: Record<string, string | undefined>,
): Promise<T> {
  const url = new URL(`${getApiBaseUrl()}${path}`);
  for (const [key, value] of Object.entries(buildParams(params))) {
    url.searchParams.set(key, value);
  }

  const attempt = async (token: string, authRetried: boolean): Promise<T> => {
    const res = await fetch(url.toString(), {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });

    if (res.status === 401 && auth.getToken && !authRetried) {
      const fresh = await auth.getToken({ skipCache: true });
      if (fresh) return attempt(fresh, true);
    }

    const body = await res.json().catch(() => null);
    if (!res.ok) {
      const message =
        typeof body === "object" &&
        body !== null &&
        "error" in body &&
        typeof (body as { error?: { message?: string } }).error?.message === "string"
          ? (body as { error: { message: string } }).error.message
          : `Analytics request failed (${res.status})`;
      throw new Error(message);
    }

    return body as T;
  };

  const token = auth.token ?? (auth.getToken ? await auth.getToken() : null);
  if (!token) throw new Error("Not authenticated");
  return attempt(token, false);
}

export async function fetchAnalyticsDashboard(
  auth: Auth,
  params: AnalyticsDashboardParams = {},
): Promise<AnalyticsDashboard> {
  return analyticsFetch<AnalyticsDashboard>(auth, "/api/v1/analytics/dashboard", {
    page: String(params.page ?? 1),
    page_size: String(params.page_size ?? 10),
    target_role: params.target_role,
    category: params.category,
    days: params.days != null ? String(params.days) : undefined,
  });
}

export async function fetchAnalyticsProgress(
  auth: Auth,
  params: Omit<AnalyticsDashboardParams, "page" | "page_size"> = {},
): Promise<AnalyticsProgress> {
  return analyticsFetch<AnalyticsProgress>(auth, "/api/v1/analytics/progress", {
    target_role: params.target_role,
    category: params.category,
    days: params.days != null ? String(params.days) : undefined,
  });
}
