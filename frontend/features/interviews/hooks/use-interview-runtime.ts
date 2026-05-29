"use client";

import { useAuth } from "@clerk/nextjs";
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

export function useInterviewRuntime(sessionId: string) {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  return useQuery({
    queryKey: ["interview-runtime", sessionId],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return fetchInterviewSessionState(token, sessionId);
    },
    enabled: isLoaded && isSignedIn && Boolean(sessionId),
    staleTime: 60_000,
    refetchOnWindowFocus: false,
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
      item.question.id === body.question_id
        ? { ...item, answer: response.answer }
        : item,
    ),
  };
}

export function useSubmitInterviewAnswer(sessionId: string) {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const runtimeKey = ["interview-runtime", sessionId] as const;

  return useMutation({
    mutationFn: async (body: SubmitAnswerRequest) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return submitInterviewAnswer(token, sessionId, body);
    },
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
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation<CompleteInterviewResponse, Error>({
    mutationFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return completeInterviewSession(token, sessionId);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["interview-runtime", sessionId] });
      await queryClient.invalidateQueries({ queryKey: ["interview-session", sessionId] });
      await queryClient.invalidateQueries({ queryKey: ["interview-sessions"] });
    },
  });
}
