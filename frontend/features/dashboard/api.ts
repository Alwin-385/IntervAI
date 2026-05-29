import { apiClient } from "@/lib/api-client";
import type { DashboardOverview } from "@/features/dashboard/types";

export async function fetchDashboardOverview(
  token: string,
): Promise<DashboardOverview> {
  return apiClient<DashboardOverview>("/api/v1/dashboard/overview", { token });
}
