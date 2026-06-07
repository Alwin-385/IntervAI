"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { deleteInterview } from "@/features/interviews/api";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useDeleteInterview() {
  const { getToken } = useAuthToken();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => deleteInterview({ getToken }, sessionId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["interview-sessions"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
    },
  });
}
