"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  completeInterviewSession,
  fetchInterviewSessionState,
  submitInterviewAnswer,
} from "@/features/interviews/api";
import type {
  CompleteInterviewResponse,
  InterviewSessionStateResponse,
  SubmitAnswerRequest,
  SubmitAnswerResponse,
} from "@/features/interviews/types";
import { useAuthToken } from "@/hooks/use-auth-token";

export function useInterviewRuntime(sessionId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuthToken();

  return useQuery({
    queryKey: ["interview-runtime", sessionId],
    queryFn: () => fetchInterviewSessionState({ getToken }, sessionId),
    enabled: isLoaded && isSignedIn && Boolean(sessionId),
    staleTime: 30_000,
    refetchOnWindowFocus: true,
  });
}

function mergeSubmitResponse(
  previous: InterviewSessionStateResponse,
  body: SubmitAnswerRequest,
  response: SubmitAnswerResponse,
): InterviewSessionStateResponse {
  return {
    ...previous,
    progress: response.progress,
    questions: previous.questions.map((item) =>
      item.question.id === body.question_id ? { ...item, answer: response.answer } : item,
    ),
  };
}

export function useSubmitInterviewAnswer(sessionId: string) {
  const { getToken } = useAuthToken();
  const queryClient = useQueryClient();
  const runtimeKey = ["interview-runtime", sessionId] as const;

  return useMutation({
    mutationFn: (body: SubmitAnswerRequest) => submitInterviewAnswer({ getToken }, sessionId, body),
    onSuccess: (response, body) => {
      const previous = queryClient.getQueryData<InterviewSessionStateResponse>(runtimeKey);
      if (!previous) return;
      queryClient.setQueryData(runtimeKey, mergeSubmitResponse(previous, body, response));
    },
    onSettled: async (_data, _err, body) => {
      if (body?.autosave) return;
      await queryClient.invalidateQueries({ queryKey: runtimeKey });
      await queryClient.invalidateQueries({ queryKey: ["interview-session", sessionId] });
      await queryClient.invalidateQueries({ queryKey: ["interview-sessions"] });
    },
  });
}

export function useCompleteInterview(sessionId: string) {
  const { getToken } = useAuthToken();
  const queryClient = useQueryClient();

  return useMutation<CompleteInterviewResponse, Error>({
    mutationFn: () => completeInterviewSession({ getToken }, sessionId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["interview-runtime", sessionId] });
      await queryClient.invalidateQueries({ queryKey: ["interview-session", sessionId] });
      await queryClient.invalidateQueries({ queryKey: ["interview-sessions"] });
    },
  });
}
