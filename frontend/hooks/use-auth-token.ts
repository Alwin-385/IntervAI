"use client";

import { useAuth } from "@clerk/nextjs";
import { useCallback } from "react";

import { createTokenRefresh, requireAuthToken } from "@/lib/auth-client";

export function useAuthToken() {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  const refreshToken = useCallback(createTokenRefresh(getToken), [getToken]);

  const requireToken = useCallback(() => requireAuthToken(getToken), [getToken]);

  return {
    getToken,
    refreshToken,
    requireToken,
    isLoaded,
    isSignedIn,
  };
}
