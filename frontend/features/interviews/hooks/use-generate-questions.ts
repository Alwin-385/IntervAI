"use client";

import { useAuth } from "@clerk/nextjs";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useEffect, useState } from "react";

import { generateInterviewQuestions } from "@/features/interviews/api";
import { useBackgroundJob } from "@/features/jobs/hooks/use-background-job";
import type { InterviewQuestionDetail } from "@/features/interviews/types";

export function useGenerateQuestions(sessionId: string) {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const questionsKey = ["interview-questions", sessionId] as const;
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  const jobQuery = useBackgroundJob(activeJobId, Boolean(activeJobId));

  useEffect(() => {
    if (jobQuery.data?.status === "completed" && activeJobId) {
      queryClient.invalidateQueries({ queryKey: questionsKey });
      setActiveJobId(null);
      toast.success("Interview questions are ready");
    }
    if (jobQuery.data?.status === "failed" && activeJobId) {
      setActiveJobId(null);
      toast.error(jobQuery.data.error_message ?? "Question generation failed");
    }
  }, [
    jobQuery.data?.status,
    jobQuery.data?.error_message,
    activeJobId,
    queryClient,
    questionsKey,
  ]);

  const mutation = useMutation({
    mutationFn: async (replaceExisting?: boolean) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return generateInterviewQuestions(token, sessionId, replaceExisting ?? true);
    },
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: questionsKey });
      const previous = queryClient.getQueryData<InterviewQuestionDetail[]>(questionsKey);
      queryClient.setQueryData(questionsKey, []);
      return { previous };
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(questionsKey, context.previous);
      }
    },
    onSuccess: (data) => {
      if (data.status === "processing" && data.job_id) {
        setActiveJobId(data.job_id);
        return;
      }
      queryClient.setQueryData(questionsKey, data.questions);
    },
  });

  return {
    ...mutation,
    isGenerating: mutation.isPending || Boolean(activeJobId),
    jobProgress: jobQuery.data?.progress_percent ?? 0,
    jobMessage: jobQuery.data?.progress_message ?? null,
  };
}
