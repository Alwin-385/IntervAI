"use client";

import { motion } from "framer-motion";
import { Calendar, FileText, HardDrive, RefreshCw, Trash2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatFileSize } from "@/features/resumes/api";
import type { Resume } from "@/features/resumes/types";

interface ResumeCardProps {
  resume: Resume;
  onReplace?: () => void;
  onDelete?: () => void;
  isPrimary?: boolean;
}

const statusVariant: Record<
  Resume["status"],
  "default" | "secondary" | "success" | "warning"
> = {
  uploaded: "secondary",
  processing: "warning",
  ready: "success",
  failed: "default",
};

export function ResumeCard({
  resume,
  onReplace,
  onDelete,
  isPrimary,
}: ResumeCardProps) {
  const uploadedAt = new Date(resume.created_at).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      layout
    >
      <Card
        className={`glass-card border-border/50 ${isPrimary ? "ring-1 ring-primary/40" : ""}`}
      >
        <CardHeader className="flex flex-row items-start justify-between gap-4 pb-3">
          <div className="flex gap-3">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-red-500/15">
              <FileText className="h-6 w-6 text-red-400" />
            </div>
            <div>
              <CardTitle className="text-lg">{resume.title}</CardTitle>
              <CardDescription className="mt-1 line-clamp-1">
                {resume.file_name}
              </CardDescription>
            </div>
          </div>
          <Badge variant={statusVariant[resume.status]} className="capitalize shrink-0">
            {resume.status}
          </Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <HardDrive className="h-3.5 w-3.5" />
              {formatFileSize(resume.file_size_bytes)}
            </span>
            <span className="flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" />
              {uploadedAt}
            </span>
          </div>
          {resume.content_text && (
            <p className="line-clamp-2 rounded-lg bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
              {resume.content_text.slice(0, 200)}
              {resume.content_text.length > 200 ? "…" : ""}
            </p>
          )}
          <div className="flex flex-wrap gap-2">
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
  );
}
