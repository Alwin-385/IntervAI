/**
 * Unit tests for the API client utility.
 */

import { apiClient, ApiError } from "@/lib/api-client";

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock env module
jest.mock("@/lib/env", () => ({
  getApiBaseUrl: () => "http://localhost:8000",
}));

afterEach(() => {
  mockFetch.mockReset();
});

describe("apiClient", () => {
  it("sends GET request to the correct URL", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => "application/json" },
      json: async () => ({ status: "healthy" }),
    });

    const result = await apiClient("/api/v1/health", {});
    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url] = mockFetch.mock.calls[0];
    expect(url).toContain("/api/v1/health");
    expect(result).toEqual({ status: "healthy" });
  });

  it("appends query params to URL", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => "application/json" },
      json: async () => ({ items: [], total: 0 }),
    });

    await apiClient("/api/v1/resumes", { params: { page: "2", page_size: "10" } });
    const [url] = mockFetch.mock.calls[0];
    expect(url).toContain("page=2");
    expect(url).toContain("page_size=10");
  });

  it("attaches Authorization header when token provided", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => "application/json" },
      json: async () => ({}),
    });

    await apiClient("/api/v1/me", { token: "my-token-abc" });
    const [, options] = mockFetch.mock.calls[0];
    expect(options.headers["Authorization"]).toBe("Bearer my-token-abc");
  });

  it("throws ApiError on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: "Not Found",
      headers: { get: () => "application/json" },
      json: async () => ({ detail: "not found" }),
    });

    await expect(apiClient("/api/v1/resumes/missing-id", {})).rejects.toBeInstanceOf(ApiError);
  });

  it("ApiError has the correct status code", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 422,
      statusText: "Unprocessable Entity",
      headers: { get: () => "application/json" },
      json: async () => ({ detail: "validation error" }),
    });

    try {
      await apiClient("/api/v1/resumes", {});
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      expect((err as ApiError).status).toBe(422);
    }
  });

  it("throws ApiError on network failure", async () => {
    mockFetch.mockRejectedValueOnce(new TypeError("Failed to fetch"));

    await expect(apiClient("/api/v1/health", {})).rejects.toBeInstanceOf(ApiError);
  });

  it("returns plain text when content-type is not json", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => "text/plain" },
      text: async () => "pong",
    });

    const result = await apiClient<string>("/ping", {});
    expect(result).toBe("pong");
  });
});
