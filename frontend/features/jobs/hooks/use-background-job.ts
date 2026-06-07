"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchJob } from "@/features/jobs/api";
import { TERMINAL_JOB_STATUSES } from "@/features/jobs/types";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useBackgroundJob(jobId: string | null | undefined, enabled = true) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["background-job", jobId],
    queryFn: () => {
      if (!jobId) throw new Error("Not authenticated");
      return fetchJob({ getToken }, jobId);
    },
    enabled: isLoaded && isSignedIn && Boolean(jobId) && enabled,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status) return 800;
      return TERMINAL_JOB_STATUSES.includes(status) ? false : 800;
    },
    staleTime: 0,
  });
}
