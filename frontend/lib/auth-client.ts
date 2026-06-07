/** Client-side Clerk token helpers for authenticated API calls. */

export type ClerkGetToken = (options?: { skipCache?: boolean }) => Promise<string | null>;

export type TokenRefresh = () => Promise<string | null>;

export function createTokenRefresh(getToken: ClerkGetToken): TokenRefresh {
  return () => getToken({ skipCache: true });
}

export async function requireAuthToken(getToken: ClerkGetToken): Promise<string> {
  const token = await getToken();
  if (!token) throw new Error("Not authenticated");
  return token;
}

/** fetch wrapper with a single 401 retry using a fresh Clerk token. */
export async function fetchWithAuth(
  token: string,
  url: string,
  init: RequestInit | undefined,
  refreshToken?: TokenRefresh,
): Promise<Response> {
  const attempt = async (authToken: string, retried: boolean): Promise<Response> => {
    const headers = new Headers(init?.headers);
    headers.set("Authorization", `Bearer ${authToken}`);

    const response = await fetch(url, {
      ...init,
      headers,
      cache: init?.cache ?? "no-store",
    });

    if (response.status === 401 && refreshToken && !retried) {
      const freshToken = await refreshToken();
      if (freshToken) {
        return attempt(freshToken, true);
      }
    }

    return response;
  };

  return attempt(token, false);
}
