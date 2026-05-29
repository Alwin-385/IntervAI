"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ArrowLeft, RefreshCw, Sparkles } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { AnalysisProgressPanel } from "@/features/resume-analysis/components/analysis-progress";
import { AnalysisResults } from "@/features/resume-analysis/components/analysis-results";
import { TargetRolePicker } from "@/features/resume-analysis/components/target-role-picker";
import {
  useResumeAnalysis,
  useStartResumeAnalysis,
} from "@/features/resume-analysis/hooks/use-resume-analysis";
import { useResume } from "@/features/resumes/hooks/use-resume";
import { normalizeResumeStatus } from "@/features/resumes/utils";

interface ResumeAnalysisPageProps {
  resumeId: string;
}

function hasAnalyzableText(resume: {
  cleaned_text?: string | null;
  content_text?: string | null;
  extracted_data?: unknown;
  text_chunks?: unknown[] | null;
}): boolean {
  if (resume.cleaned_text?.trim()) return true;
  if (resume.content_text?.trim()) return true;
  if (resume.extracted_data && typeof resume.extracted_data === "object") {
    const d = resume.extracted_data as Record<string, unknown>;
    const lists = ["skills", "experience", "education", "projects"] as const;
    if (lists.some((k) => Array.isArray(d[k]) && (d[k] as unknown[]).length > 0)) {
      return true;
    }
  }
  if (resume.text_chunks && resume.text_chunks.length > 0) return true;
  return false;
}

export function ResumeAnalysisPage({ resumeId }: ResumeAnalysisPageProps) {
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const { data: resume, isLoading: resumeLoading, refetch: refetchResume } = useResume(resumeId);
  const { data: analysis, isLoading: analysisLoading, isError, error, refetch } =
    useResumeAnalysis(resumeId);
  const startAnalysis = useStartResumeAnalysis(resumeId);

  const status = resume ? normalizeResumeStatus(resume.status) : null;
  const extractionReady = status === "completed";
  const textReady = resume ? hasAnalyzableText(resume) : false;
  const canAnalyze = extractionReady && textReady;

  const isProcessing =
    analysis?.status === "pending" || analysis?.status === "processing";
  const isComplete = analysis?.status === "completed" && analysis.analysis;
  const isFailed = analysis?.status === "failed";

  const blockReason = useMemo(() => {
    if (resumeLoading) return null;
    if (!extractionReady) return "Wait until the resume shows Ready on the Resumes page.";
    if (!textReady)
      return "Extraction data is missing. Re-extract the PDF from Resumes, then return here.";
    return null;
  }, [resumeLoading, extractionReady, textReady]);

  const handleAnalyze = () => {
    if (!canAnalyze) {
      toast.error(blockReason ?? "Resume not ready for analysis");
      return;
    }
    startAnalysis.mutate(
      { target_role: targetRole.trim() || undefined },
      {
        onSuccess: (data) => {
          if (data.status === "completed") {
            toast.success("Analysis complete");
          } else if (data.status === "failed") {
            toast.error(data.error_message ?? "Analysis failed");
          } else {
            toast.success("Analysis started");
            void refetch();
          }
        },
        onError: (err) =>
          toast.error(err instanceof Error ? err.message : "Failed to start analysis"),
      },
    );
  };

  const handleForceRetry = () => {
    handleAnalyze();
  };

  return (
    <div className="space-y-8 p-4 md:p-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link
            href="/dashboard/resumes"
            className="mb-3 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to resumes
          </Link>
          <div className="flex items-center gap-2 text-primary">
            <Sparkles className="h-5 w-5" />
            <span className="text-sm font-medium">AI Resume Analyzer</span>
          </div>
          {resumeLoading ? (
            <Skeleton className="mt-2 h-8 w-64" />
          ) : (
            <h1 className="mt-1 text-2xl font-bold tracking-tight">
              {resume?.extracted_data?.name ?? resume?.title ?? "Resume analysis"}
            </h1>
          )}
          {resume?.file_name && (
            <p className="mt-1 text-sm text-muted-foreground">{resume.file_name}</p>
          )}
        </div>

        <div className="flex w-full max-w-xl flex-col gap-3 sm:max-w-2xl">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start">
            <TargetRolePicker
              value={targetRole}
              onChange={setTargetRole}
              disabled={startAnalysis.isPending}
            />
          <Button
            onClick={handleAnalyze}
            disabled={startAnalysis.isPending || !canAnalyze}
            className="h-10 shrink-0 gap-2 sm:mt-6"
            size="default"
          >
            <Sparkles className={`h-4 w-4 ${startAnalysis.isPending ? "animate-spin" : ""}`} />
            {startAnalysis.isPending ? "Analyzing…" : isProcessing ? "Analyzing…" : "Analyze resume"}
          </Button>
          </div>
        </div>
      </div>

      {blockReason && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
          <span>{blockReason}</span>
          {!textReady && extractionReady && (
            <Button variant="outline" size="sm" className="gap-2" asChild>
              <Link href="/dashboard/resumes">
                <RefreshCw className="h-3.5 w-3.5" />
                Re-extract on Resumes
              </Link>
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => void refetchResume()}
            className="text-amber-100"
          >
            Refresh status
          </Button>
        </div>
      )}

      {isError && (
        <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {(error as Error).message}
        </p>
      )}

      {analysisLoading && !analysis && !isProcessing && <AnalysisPageSkeleton />}

      {!analysisLoading && !analysis && !isProcessing && !startAnalysis.isPending && canAnalyze && (
        <div className="glass-card rounded-2xl border border-dashed border-primary/30 bg-primary/5 py-16 text-center">
          <Sparkles className="mx-auto mb-4 h-10 w-10 text-primary" />
          <p className="text-lg font-medium">Ready for AI analysis</p>
          <p className="mt-2 text-sm text-muted-foreground">
            Click <strong>Analyze resume</strong> for ATS scoring, role readiness, and recruiter-style
            feedback.
          </p>
        </div>
      )}

      {isProcessing && (
        <>
          <AnalysisProgressPanel progress={analysis?.progress ?? null} />
          <p className="text-center text-xs text-muted-foreground">
            Usually finishes in under a minute. If this screen does not change, click{" "}
            <button
              type="button"
              className="font-medium text-primary underline-offset-2 hover:underline"
              onClick={handleForceRetry}
            >
              Analyze resume
            </button>{" "}
            again.
          </p>
        </>
      )}

      {isFailed && (
        <div className="space-y-3">
          <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {analysis?.error_message ?? "Analysis failed. Try again."}
          </p>
          <Button variant="default" onClick={handleForceRetry} disabled={!canAnalyze} className="gap-2">
            <Sparkles className="h-4 w-4" />
            Analyze resume again
          </Button>
        </div>
      )}

      {isComplete && analysis.analysis && (
        <AnalysisResults analysis={analysis.analysis} />
      )}
    </div>
  );
}

function AnalysisPageSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-36 w-full rounded-2xl" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-xl" />
        ))}
      </div>
    </div>
  );
}
