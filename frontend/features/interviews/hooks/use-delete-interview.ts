"use client";

import { useAuth } from "@clerk/nextjs";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { deleteInterview } from "@/features/interviews/api";

export function useDeleteInterview() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (sessionId: string) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return deleteInterview(token, sessionId);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["interview-sessions"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
    },
  });
}
