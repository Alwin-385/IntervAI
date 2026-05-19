import { apiClient } from "@/lib/api-client";

export interface HealthResponse {
  status: "healthy";
  service: string;
  version: string;
  environment: string;
  timestamp: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return apiClient<HealthResponse>("/api/v1/health");
}
