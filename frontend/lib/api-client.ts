import { getApiBaseUrl } from "@/lib/env";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = RequestInit & {
  params?: Record<string, string>;
  token?: string | null;
  timeoutMs?: number;
};

export async function apiClient<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, token, timeoutMs, ...init } = options;
  const url = new URL(`${getApiBaseUrl()}${path}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.set(key, value);
    });
  }

  const authHeaders: Record<string, string> = {};
  if (token) {
    authHeaders.Authorization = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(url.toString(), {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...authHeaders,
        ...headers,
      },
      cache: "no-store",
      ...(timeoutMs ? { signal: AbortSignal.timeout(timeoutMs) } : {}),
    });
  } catch (err) {
    if (err instanceof Error && err.name === "TimeoutError") {
      throw new ApiError("Request timed out. Check that the backend is running and try again.", 0);
    }
    throw new ApiError(
      `Cannot reach API at ${getApiBaseUrl()}. From c:\\IntervAI run .\\scripts\\start-backend.ps1, then open http://127.0.0.1:8000/api/v1/health (use 127.0.0.1, not localhost, on Windows).`,
      0,
    );
  }

  const contentType = response.headers.get("content-type");
  const body = contentType?.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof body === "object" &&
      body !== null &&
      "error" in body &&
      typeof (body as { error?: { message?: string } }).error?.message === "string"
        ? (body as { error: { message: string } }).error.message
        : `API request failed: ${response.status} ${response.statusText}`;

    throw new ApiError(message, response.status, body);
  }

  return body as T;
}
