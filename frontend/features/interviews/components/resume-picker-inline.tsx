"use client";

import { FileText, AlertCircle } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { useResumes } from "@/features/resumes/hooks/use-resumes";

interface ResumePickerInlineProps {
  value: string | null;
  onChange: (resumeId: string | null) => void;
}

export function ResumePickerInline({ value, onChange }: ResumePickerInlineProps) {
  const { data, isLoading } = useResumes(1, 10);
  const resumes = (data?.items ?? []).filter((r) => r.status === "completed");

  if (isLoading) {
    return <Skeleton className="h-20 w-full rounded-xl" />;
  }

  if (resumes.length === 0) {
    return (
      <div className="flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-100">
        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
        <div>
          <p className="font-medium">No completed resume yet</p>
          <p className="mt-1 text-xs text-amber-200/80">
            Upload a resume from the Resumes page and wait for it to finish extraction, then return here.
            Or pick another category to continue.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2 rounded-xl border border-border/60 bg-card/60 p-4">
      <p className="text-xs font-medium text-muted-foreground">
        Pick the resume to base questions on
      </p>
      <div className="grid gap-2 sm:grid-cols-2">
        {resumes.map((resume) => {
          const active = value === resume.id;
          return (
            <button
              key={resume.id}
              type="button"
              onClick={() => onChange(resume.id)}
              className={cn(
                "flex items-start gap-3 rounded-lg border p-3 text-left text-sm transition-colors",
                active
                  ? "border-primary/70 bg-primary/10"
                  : "border-border/60 hover:border-primary/40 hover:bg-primary/5",
              )}
            >
              <FileText
                className={cn(
                  "mt-0.5 h-4 w-4 shrink-0",
                  active ? "text-primary" : "text-muted-foreground",
                )}
              />
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">
                  {resume.title ?? resume.file_name ?? "Resume"}
                </p>
                {resume.file_name && resume.file_name !== resume.title && (
                  <p className="truncate text-xs text-muted-foreground">
                    {resume.file_name}
                  </p>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
