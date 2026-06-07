import { getApiBaseUrl } from "@/lib/env";

function isLocalApiUrl(apiUrl: string): boolean {
  return (
    apiUrl.includes("127.0.0.1") || apiUrl.includes("localhost") || apiUrl.startsWith("http://")
  );
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Ping /health until Render free tier is awake (no-op locally). */
export async function ensureBackendAwake(maxAttempts = 6): Promise<void> {
  const base = getApiBaseUrl();
  if (isLocalApiUrl(base)) return;

  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    try {
      const res = await fetch(`${base}/api/v1/health`, { cache: "no-store" });
      if (res.ok) return;
    } catch {
      // Render may still be starting
    }
    await sleep(attempt === 0 ? 2000 : 4000);
  }
}
