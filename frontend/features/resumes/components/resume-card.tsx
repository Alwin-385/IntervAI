"use client";

import { useAuth } from "@clerk/nextjs";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  AlertCircle,
  Calendar,
  CheckCircle2,
  ExternalLink,
  FileText,
  HardDrive,
  Loader2,
  RefreshCw,
  Sparkles,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ResumeCardSummary } from "@/features/resumes/components/resume-card-summary";
import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard-overview";
import { ExtractionProgress } from "@/features/resumes/components/extraction-progress";
import { ExtractionViewDialog } from "@/features/resumes/components/extraction-view-dialog";
import { formatFileSize, retryExtraction } from "@/features/resumes/api";
import type { Resume, ResumeStatus } from "@/features/resumes/types";
import { hasExtractedContent, normalizeResumeStatus } from "@/features/resumes/utils";

interface ResumeCardProps {
  resume: Resume;
  onReplace?: () => void;
  onDelete?: () => void;
  isPrimary?: boolean;
}

const statusLabels: Record<ResumeStatus, string> = {
  queued: "Queued",
  extracting_resume: "Extracting",
  completed: "Ready",
  failed: "Failed",
};

const statusVariant: Record<ResumeStatus, "default" | "secondary" | "success" | "warning"> = {
  queued: "secondary",
  extracting_resume: "warning",
  completed: "success",
  failed: "default",
};

export function ResumeCard({ resume, onReplace, onDelete, isPrimary }: ResumeCardProps) {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const [detailsOpen, setDetailsOpen] = useState(false);
  const status = normalizeResumeStatus(resume.status);
  const isProcessing = status === "queued" || status === "extracting_resume";
  const extracted = resume.extracted_data;
  const showFullView =
    status === "completed" &&
    (Boolean(extracted && hasExtractedContent(extracted)) || Boolean(resume.cleaned_text));

  const retryMutation = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return retryExtraction(token, resume.id);
    },
    onSuccess: async () => {
      toast.success("Extraction started");
      await queryClient.invalidateQueries({ queryKey: ["resumes"] });
      await queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
    onError: (err) => {
      toast.error(err instanceof Error ? err.message : "Retry failed");
    },
  });

  const uploadedAt = new Date(resume.created_at).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <>
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} layout>
        <Card
          className={`glass-card border-border/50 ${isPrimary ? "ring-1 ring-primary/40" : ""}`}
        >
          <CardHeader className="flex flex-row items-start justify-between gap-4 pb-3">
            <div className="flex gap-3">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-red-500/15">
                <FileText className="h-6 w-6 text-red-400" />
              </div>
              <div>
                <CardTitle className="text-lg">{extracted?.name ?? resume.title}</CardTitle>
                <CardDescription className="mt-1 line-clamp-1">{resume.file_name}</CardDescription>
              </div>
            </div>
            <Badge variant={statusVariant[status]} className="shrink-0 gap-1 capitalize">
              {isProcessing && <Loader2 className="h-3 w-3 animate-spin" />}
              {status === "completed" && <CheckCircle2 className="h-3 w-3" />}
              {statusLabels[status]}
            </Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            {isProcessing && <ExtractionProgress status={status} />}

            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <HardDrive className="h-3.5 w-3.5" />
                {formatFileSize(resume.file_size_bytes)}
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5" />
                {uploadedAt}
              </span>
              {resume.text_chunks && resume.text_chunks.length > 0 && (
                <span>{resume.text_chunks.length} chunks indexed</span>
              )}
            </div>

            {status === "failed" && resume.extraction_error && (
              <div className="flex gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive">
                <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                <span>{resume.extraction_error}</span>
              </div>
            )}

            {status === "completed" && extracted && hasExtractedContent(extracted) && (
              <ResumeCardSummary data={extracted} />
            )}

            <div className="flex flex-wrap gap-2">
              {status === "completed" && (
                <Button variant="default" size="sm" className="gap-2" asChild>
                  <Link href={`/dashboard/resumes/${resume.id}/analysis`}>
                    <Sparkles className="h-3.5 w-3.5" />
                    Analyze resume
                  </Link>
                </Button>
              )}
              {showFullView && (
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-2"
                  onClick={() => setDetailsOpen(true)}
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                  View full extraction
                </Button>
              )}
              {(status === "failed" || status === "queued" || status === "completed") && (
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-2"
                  disabled={retryMutation.isPending || isProcessing}
                  onClick={() => retryMutation.mutate()}
                >
                  <RefreshCw
                    className={`h-3.5 w-3.5 ${retryMutation.isPending ? "animate-spin" : ""}`}
                  />
                  {status === "failed"
                    ? "Retry extraction"
                    : status === "completed"
                      ? "Re-extract"
                      : "Run extraction"}
                </Button>
              )}
              {onReplace && (
                <Button variant="outline" size="sm" onClick={onReplace} className="gap-2">
                  <RefreshCw className="h-3.5 w-3.5" />
                  Replace PDF
                </Button>
              )}
              {onDelete && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onDelete}
                  className="gap-2 text-destructive hover:text-destructive"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Delete
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <ExtractionViewDialog
        resume={resume}
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
      />
    </>
  );
}
