"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchResumes } from "@/features/resumes/api";
import { normalizeResumeList } from "@/features/resumes/utils";
import { EXTRACTION_POLL_STATUSES } from "@/features/resumes/types";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useResumes(page = 1, pageSize = 20) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["resumes", page, pageSize],
    queryFn: async () => {
      const data = await fetchResumes({ getToken }, page, pageSize);
      return normalizeResumeList(data);
    },
    enabled: isLoaded && isSignedIn,
    staleTime: 2_000,
    refetchInterval: (query) => {
      const items = query.state.data?.items ?? [];
      const needsPoll = items.some((r) => EXTRACTION_POLL_STATUSES.includes(r.status));
      return needsPoll ? 1_000 : false;
    },
  });
}
