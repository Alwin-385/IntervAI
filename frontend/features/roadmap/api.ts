import { getApiBaseUrl } from "@/lib/env";
import type { GeneratedRoadmap } from "@/features/roadmap/types";

export class RoadmapApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: unknown,
  ) {
    super(message);
    this.name = "RoadmapApiError";
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  let body: unknown = null;
  try {
    body = await res.json();
  } catch {
    body = null;
  }
  if (!res.ok) throw new RoadmapApiError(parseError(body), res.status, body);
  return body as T;
}

export async function generateRoadmap(
  token: string,
  targetRole?: string,
): Promise<GeneratedRoadmap> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/roadmap/generate`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ target_role: targetRole ?? null, force_regenerate: true }),
  });
  return handleResponse<GeneratedRoadmap>(res);
}

export async function fetchRoadmap(
  token: string,
  targetRole?: string,
): Promise<GeneratedRoadmap | null> {
  const query = targetRole ? `?target_role=${encodeURIComponent(targetRole)}` : "";
  const res = await fetch(`${getApiBaseUrl()}/api/v1/roadmap${query}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (res.status === 404) return null;
  const data = await handleResponse<GeneratedRoadmap | null>(res);
  return data;
}

export async function updateRoadmapItem(
  token: string,
  roadmapId: string,
  itemId: string,
  completed: boolean,
): Promise<GeneratedRoadmap> {
  const res = await fetch(
    `${getApiBaseUrl()}/api/v1/roadmap/${roadmapId}/items/${itemId}`,
    {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ completed }),
    },
  );
  return handleResponse<GeneratedRoadmap>(res);
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
  return "Roadmap request failed";
}
