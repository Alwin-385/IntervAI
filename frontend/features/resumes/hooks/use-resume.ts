"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { fetchResume } from "@/features/resumes/api";

export function useResume(resumeId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: ["resume", resumeId],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchResume(token, resumeId);
    },
    enabled: isLoaded && isSignedIn && Boolean(resumeId),
  });
}
