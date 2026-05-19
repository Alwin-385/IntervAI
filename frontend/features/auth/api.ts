import { apiClient } from "@/lib/api-client";

import type { MeResponse } from "./types";

export async function fetchMe(token: string): Promise<MeResponse> {
  return apiClient<MeResponse>("/api/v1/me", { token });
}

export async function fetchMeAlias(token: string): Promise<MeResponse> {
  return apiClient<MeResponse>("/api/me", { token });
}
