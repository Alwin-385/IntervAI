"use client";

import { useAuth } from "@clerk/nextjs";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createInterview } from "@/features/interviews/api";
import type { InterviewCreateRequest } from "@/features/interviews/types";

export function useCreateInterview() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (body: InterviewCreateRequest) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return createInterview(token, body);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["interview-sessions"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
    },
  });
}
