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
};

export async function apiClient<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { params, headers, token, ...init } = options;
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

  const response = await fetch(url.toString(), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...headers,
    },
    cache: "no-store",
  });

  const contentType = response.headers.get("content-type");
  const body =
    contentType?.includes("application/json")
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
