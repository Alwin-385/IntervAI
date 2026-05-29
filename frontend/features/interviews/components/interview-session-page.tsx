"use client";

import Link from "next/link";
import { ArrowLeft, Loader2, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { InterviewSessionPlayer } from "@/features/interviews/components/interview-session-player";
import { useInterviewRuntime } from "@/features/interviews/hooks/use-interview-runtime";
import { ApiError } from "@/lib/api-client";

interface InterviewSessionPageProps {
  sessionId: string;
}

export function InterviewSessionPage({ sessionId }: InterviewSessionPageProps) {
  const { data, isLoading, isError, error } = useInterviewRuntime(sessionId);

  if (isLoading) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    );
  }

  if (isError || !data) {
    const message =
      error instanceof ApiError
        ? error.message
        : error instanceof Error
          ? error.message
          : "Unable to load interview session.";
    const needsQuestions =
      error instanceof ApiError &&
      (error.status === 422 || message.toLowerCase().includes("no questions"));

    return (
      <div className="mx-auto max-w-2xl space-y-4 p-6">
        <Link
          href={`/dashboard/interviews/${sessionId}`}
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to interview details
        </Link>
        <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {message}
        </p>
        {needsQuestions && (
          <Button asChild className="gap-2">
            <Link href={`/dashboard/interviews/${sessionId}`}>
              <Sparkles className="h-4 w-4" />
              Generate questions first
            </Link>
          </Button>
        )}
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between border-b border-border/60 px-4 py-3 md:px-8">
        <Link
          href={`/dashboard/interviews/${sessionId}`}
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Exit session
        </Link>
        <Button asChild variant="ghost" size="sm">
          <Link href={`/dashboard/interviews/${sessionId}`}>Details</Link>
        </Button>
      </div>
      <InterviewSessionPlayer sessionId={sessionId} runtime={data} />
    </div>
  );
}
