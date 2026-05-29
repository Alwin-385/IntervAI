import { getApiBaseUrl } from "@/lib/env";
import type { WeakAreasAnalytics } from "@/features/weak-areas/types";

export class WeakAreasApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: unknown,
  ) {
    super(message);
    this.name = "WeakAreasApiError";
  }
}

export async function fetchWeakAreasAnalytics(token: string): Promise<WeakAreasAnalytics> {
  let res: Response;
  try {
    res = await fetch(`${getApiBaseUrl()}/api/v1/analytics/weak-areas`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
  } catch {
    throw new WeakAreasApiError(
      "Cannot reach the API. Start the backend with .\\scripts\\start-backend.ps1",
      0,
    );
  }

  let body: unknown = null;
  try {
    body = await res.json();
  } catch {
    body = null;
  }
  if (!res.ok) {
    throw new WeakAreasApiError(parseError(body), res.status, body);
  }
  return body as WeakAreasAnalytics;
}

function parseError(body: unknown): string {
  if (
    typeof body === "object" &&
    body !== null &&
    "error" in body &&
    typeof (body as { error?: { message?: string } }).error?.message === "string"
  ) {
    return (body as { error: { message: string } }).error.message;
  }
  return "Could not load weak areas analytics";
}
