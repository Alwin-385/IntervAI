import { getApiBaseUrl } from "@/lib/env";
import type {
  AnalyticsDashboard,
  AnalyticsDashboardParams,
  AnalyticsProgress,
} from "@/features/analytics/types";

function buildQuery(params: Record<string, string | number | undefined>): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") q.set(k, String(v));
  }
  const s = q.toString();
  return s ? `?${s}` : "";
}

async function handleResponse<T>(res: Response): Promise<T> {
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const msg =
      typeof body === "object" &&
      body !== null &&
      "error" in body &&
      typeof (body as { error?: { message?: string } }).error?.message === "string"
        ? (body as { error: { message: string } }).error.message
        : "Analytics request failed";
    throw new Error(msg);
  }
  return body as T;
}

export async function fetchAnalyticsDashboard(
  token: string,
  params: AnalyticsDashboardParams = {},
): Promise<AnalyticsDashboard> {
  const query = buildQuery({
    page: params.page ?? 1,
    page_size: params.page_size ?? 10,
    target_role: params.target_role,
    category: params.category,
    days: params.days,
  });
  const res = await fetch(`${getApiBaseUrl()}/api/v1/analytics/dashboard${query}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return handleResponse<AnalyticsDashboard>(res);
}

export async function fetchAnalyticsProgress(
  token: string,
  params: Omit<AnalyticsDashboardParams, "page" | "page_size"> = {},
): Promise<AnalyticsProgress> {
  const query = buildQuery({
    target_role: params.target_role,
    category: params.category,
    days: params.days,
  });
  const res = await fetch(`${getApiBaseUrl()}/api/v1/analytics/progress${query}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return handleResponse<AnalyticsProgress>(res);
}
