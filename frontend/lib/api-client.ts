import { getApiBaseUrl } from "@/lib/env";
import { createTokenRefresh, type ClerkGetToken, type TokenRefresh } from "@/lib/auth-client";

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
  /** Pass a cached token, or omit and use getToken */
  token?: string | null;
  /** Clerk getToken — fetches a session JWT and auto-retries on 401 with skipCache */
  getToken?: ClerkGetToken;
  timeoutMs?: number;
  refreshToken?: TokenRefresh;
  /** Retry transient network failures (Render cold start / OOM restart). Default 2 on production. */
  networkRetries?: number;
};

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isLocalApiUrl(apiUrl: string): boolean {
  return (
    apiUrl.includes("127.0.0.1") || apiUrl.includes("localhost") || apiUrl.startsWith("http://")
  );
}

export async function apiClient<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, token, getToken, timeoutMs, refreshToken, networkRetries, ...init } =
    options;
  const refresh = refreshToken ?? (getToken ? createTokenRefresh(getToken) : undefined);
  const initialToken = token ?? (getToken ? await getToken() : null);
  const apiUrl = getApiBaseUrl();
  const maxNetworkRetries = networkRetries ?? (isLocalApiUrl(apiUrl) ? 0 : 2);

  const send = async (
    authToken: string | null | undefined,
    authRetried: boolean,
    networkAttempt = 0,
  ): Promise<T> => {
    const url = new URL(`${getApiBaseUrl()}${path}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.set(key, value);
      });
    }

    const authHeaders: Record<string, string> = {};
    if (authToken) {
      authHeaders.Authorization = `Bearer ${authToken}`;
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
        if (networkAttempt < maxNetworkRetries) {
          await sleep(3000 * (networkAttempt + 1));
          return send(authToken, authRetried, networkAttempt + 1);
        }
        throw new ApiError(
          "Request timed out. The analytics request may be heavy — wait a moment and try again.",
          0,
        );
      }
      if (networkAttempt < maxNetworkRetries) {
        await sleep(3000 * (networkAttempt + 1));
        return send(authToken, authRetried, networkAttempt + 1);
      }
      const isLocal = isLocalApiUrl(apiUrl);
      const hint = isLocal
        ? "From c:\\IntervAI run .\\scripts\\start-backend.ps1, then open http://127.0.0.1:8000/api/v1/health."
        : "The backend may be waking up (Render free tier). Wait 30s, open the /api/v1/health URL in a tab, then refresh.";
      throw new ApiError(`Cannot reach API at ${apiUrl}. ${hint}`, 0);
    }

    if (response.status === 401 && refresh && !authRetried) {
      const freshToken = await refresh();
      if (freshToken) {
        return send(freshToken, true, networkAttempt);
      }
    }

    if (response.status === 503 && networkAttempt < maxNetworkRetries) {
      await sleep(3000 * (networkAttempt + 1));
      return send(authToken, authRetried, networkAttempt + 1);
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
  };

  return send(initialToken, false);
}
