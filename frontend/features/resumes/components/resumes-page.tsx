"use client";

import { useAuth } from "@clerk/nextjs";
import { useQueryClient } from "@tanstack/react-query";
import { FileText } from "lucide-react";
import { useCallback, useState } from "react";
import { toast } from "sonner";

import { Skeleton } from "@/components/ui/skeleton";
import { apiClient } from "@/lib/api-client";
import { ResumeCard } from "@/features/resumes/components/resume-card";
import { ResumeUploader } from "@/features/resumes/components/resume-uploader";
import { useResumes } from "@/features/resumes/hooks/use-resumes";
import type { PaginatedResumes, Resume, ResumeUploadResponse } from "@/features/resumes/types";
import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard-overview";
import { normalizeResume } from "@/features/resumes/utils";

const LIST_KEY = ["resumes", 1, 20] as const;

export function ResumesPage() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const { data, isLoading, isError, error, refetch } = useResumes();
  const [replaceTarget, setReplaceTarget] = useState<Resume | null>(null);

  const mergeUploadedResume = useCallback(
    (uploaded: ResumeUploadResponse) => {
      const normalized = normalizeResume(uploaded);
      queryClient.setQueryData<PaginatedResumes>(LIST_KEY, (old) => {
        if (!old) {
          return {
            items: [normalized],
            total: 1,
            page: 1,
            page_size: 20,
            pages: 1,
          };
        }
        const index = old.items.findIndex((r) => r.id === normalized.id);
        const items =
          index >= 0
            ? old.items.map((r, i) => (i === index ? normalized : r))
            : [normalized, ...old.items];
        return {
          ...old,
          items,
          total: index >= 0 ? old.total : old.total + 1,
        };
      });
    },
    [queryClient],
  );

  const handleUploadSuccess = async (uploaded: ResumeUploadResponse) => {
    setReplaceTarget(null);
    mergeUploadedResume(uploaded);
    toast.info("Extracting resume text…", { duration: 4000 });
    await queryClient.invalidateQueries({ queryKey: ["resumes"] });
    await queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    requestAnimationFrame(() => {
      document.getElementById("resume-library")?.scrollIntoView({ behavior: "smooth" });
    });
  };

  const handleDelete = async (resume: Resume) => {
    if (!confirm(`Delete "${resume.title}"?`)) return;
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      await apiClient(`/api/v1/resumes/${resume.id}`, {
        method: "DELETE",
        token,
      });
      toast.success("Resume deleted");
      await queryClient.invalidateQueries({ queryKey: ["resumes"] });
      await queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const primaryResume = data?.items[0];
  const processingCount =
    data?.items.filter(
      (r) => r.status === "queued" || r.status === "extracting_resume",
    ).length ?? 0;

  return (
    <div className="space-y-8 p-4 md:p-8">
      <div>
        <div className="mb-2 flex items-center gap-2 text-primary">
          <FileText className="h-5 w-5" />
          <span className="text-sm font-medium">Resume library</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight md:text-3xl">Upload your resume</h1>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          After upload, your resume is queued, text is extracted in the background, and
          structured sections appear on the card below (skills, experience, education, and
          more).
        </p>
      </div>

      <ResumeUploader
        replaceResume={replaceTarget}
        onSuccess={handleUploadSuccess}
        onCancelReplace={() => setReplaceTarget(null)}
      />

      <section id="resume-library">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-semibold">Your resumes</h2>
          {processingCount > 0 && (
            <span className="text-sm text-amber-400">
              {processingCount} extracting… (updates every second)
            </span>
          )}
        </div>

        {isLoading && (
          <div className="space-y-4">
            <Skeleton className="h-48 w-full rounded-2xl" />
            <Skeleton className="h-48 w-full rounded-2xl" />
          </div>
        )}

        {isError && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            <p>{(error as Error).message}</p>
            <button
              type="button"
              className="mt-2 underline"
              onClick={() => void refetch()}
            >
              Retry
            </button>
          </div>
        )}

        {!isLoading && !isError && data?.items.length === 0 && (
          <p className="rounded-xl border border-dashed border-border/60 py-12 text-center text-sm text-muted-foreground">
            No resumes yet — upload your first PDF above. Your resume card will appear here
            with live extraction status.
          </p>
        )}

        <div className="grid items-start gap-4 lg:grid-cols-2">
          {data?.items.map((resume) => (
            <ResumeCard
              key={resume.id}
              resume={resume}
              isPrimary={primaryResume?.id === resume.id}
              onReplace={() => {
                setReplaceTarget(resume);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              onDelete={() => handleDelete(resume)}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
