"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchResume } from "@/features/resumes/api";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useResume(resumeId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["resume", resumeId],
    queryFn: () => fetchResume({ getToken }, resumeId),
    enabled: isLoaded && isSignedIn && Boolean(resumeId),
  });
}
