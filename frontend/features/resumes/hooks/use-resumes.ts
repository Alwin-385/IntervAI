"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { fetchResumes } from "@/features/resumes/api";

export function useResumes(page = 1, pageSize = 20) {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: ["resumes", page, pageSize],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchResumes(token, page, pageSize);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 30_000,
  });
}
