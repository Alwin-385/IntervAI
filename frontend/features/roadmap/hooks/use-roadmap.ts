"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { useBackgroundJob } from "@/features/jobs/hooks/use-background-job";
import { fetchRoadmap, generateRoadmap, updateRoadmapItem } from "@/features/roadmap/api";
import { useAuthToken } from "@/hooks/use-auth-token";

const QUERY_KEY = ["roadmap"];

export function useRoadmap(targetRole?: string) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();
  return useQuery({
    queryKey: [...QUERY_KEY, targetRole ?? "all"],
    queryFn: () => fetchRoadmap({ getToken }, targetRole),
    enabled: isLoaded && isSignedIn,
    staleTime: 60_000,
  });
}

export function useGenerateRoadmap() {
  const { getToken } = useAuthToken();
  const qc = useQueryClient();
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const jobQuery = useBackgroundJob(activeJobId, Boolean(activeJobId));

  useEffect(() => {
    if (jobQuery.data?.status === "completed" && activeJobId) {
      qc.invalidateQueries({ queryKey: QUERY_KEY });
      setActiveJobId(null);
      toast.success("Your roadmap is ready");
    }
    if (jobQuery.data?.status === "failed" && activeJobId) {
      setActiveJobId(null);
      toast.error(jobQuery.data.error_message ?? "Roadmap generation failed");
    }
  }, [jobQuery.data?.status, jobQuery.data?.error_message, activeJobId, qc]);

  const mutation = useMutation({
    mutationFn: (targetRole?: string) => generateRoadmap({ getToken }, targetRole),
    onSuccess: (data, targetRole) => {
      if (data.status === "processing" && data.job_id) {
        setActiveJobId(data.job_id);
        return;
      }
      qc.setQueryData([...QUERY_KEY, targetRole ?? "all"], data);
    },
  });

  return {
    ...mutation,
    isGenerating: mutation.isPending || Boolean(activeJobId),
    jobProgress: jobQuery.data?.progress_percent ?? 0,
    jobMessage: jobQuery.data?.progress_message ?? null,
  };
}

export function useUpdateRoadmapItem(roadmapId: string, targetRole?: string) {
  const { getToken } = useAuthToken();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ itemId, completed }: { itemId: string; completed: boolean }) =>
      updateRoadmapItem({ getToken }, roadmapId, itemId, completed),
    onSuccess: (data) => qc.setQueryData([...QUERY_KEY, targetRole ?? "all"], data),
  });
}
