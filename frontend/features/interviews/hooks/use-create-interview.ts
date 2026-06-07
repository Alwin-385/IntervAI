"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createInterview } from "@/features/interviews/api";
import type { InterviewCreateRequest } from "@/features/interviews/types";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useCreateInterview() {
  const { getToken } = useAuthToken();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: InterviewCreateRequest) => createInterview({ getToken }, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["interview-sessions"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
    },
  });
}
