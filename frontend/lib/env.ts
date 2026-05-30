export const env = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000",
  appName: process.env.NEXT_PUBLIC_APP_NAME ?? "AI Interview Intelligence Platform",
} as const;

export function getApiBaseUrl(): string {
  return env.apiUrl.replace(/\/$/, "");
}
