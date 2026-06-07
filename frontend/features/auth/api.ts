import { apiClient } from "@/lib/api-client";
import type { ClerkGetToken, TokenRefresh } from "@/lib/auth-client";

import type { MeResponse } from "./types";

type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

export async function fetchMe(auth: Auth): Promise<MeResponse> {
  return apiClient<MeResponse>("/api/v1/me", auth);
}
