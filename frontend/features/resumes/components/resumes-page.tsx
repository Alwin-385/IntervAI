"use client";

import { useAuth } from "@clerk/nextjs";
import { useQueryClient } from "@tanstack/react-query";
import { FileText } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Skeleton } from "@/components/ui/skeleton";
import { apiClient } from "@/lib/api-client";
import { ResumeCard } from "@/features/resumes/components/resume-card";
import { ResumeUploader } from "@/features/resumes/components/resume-uploader";
import { useResumes } from "@/features/resumes/hooks/use-resumes";
import type { Resume, ResumeUploadResponse } from "@/features/resumes/types";

export function ResumesPage() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const { data, isLoading, isError, error } = useResumes();
  const [replaceTarget, setReplaceTarget] = useState<Resume | null>(null);

  const handleUploadSuccess = async (_resume: ResumeUploadResponse) => {
    setReplaceTarget(null);
    await queryClient.invalidateQueries({ queryKey: ["resumes"] });
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
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const primaryResume = data?.items[0];

  return (
    <div className="space-y-8 p-4 md:p-8">
      <div>
        <div className="mb-2 flex items-center gap-2 text-primary">
          <FileText className="h-5 w-5" />
          <span className="text-sm font-medium">Resume library</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight md:text-3xl">Upload your resume</h1>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          Secure PDF upload with validation. Replace an existing resume anytime — we keep
          metadata in sync for AI analysis in upcoming phases.
        </p>
      </div>

      <ResumeUploader
        replaceResume={replaceTarget}
        onSuccess={handleUploadSuccess}
        onCancelReplace={() => setReplaceTarget(null)}
      />

      <section>
        <h2 className="mb-4 text-lg font-semibold">Your resumes</h2>

        {isLoading && (
          <div className="space-y-4">
            <Skeleton className="h-40 w-full rounded-2xl" />
            <Skeleton className="h-40 w-full rounded-2xl" />
          </div>
        )}

        {isError && (
          <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {(error as Error).message}
          </p>
        )}

        {!isLoading && !isError && data?.items.length === 0 && (
          <p className="rounded-xl border border-dashed border-border/60 py-12 text-center text-sm text-muted-foreground">
            No resumes yet — upload your first PDF above.
          </p>
        )}

        <div className="grid gap-4 lg:grid-cols-2">
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
