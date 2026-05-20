"use client";

import { useAuth } from "@clerk/nextjs";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircle2,
  FileUp,
  Loader2,
  Upload,
  XCircle,
} from "lucide-react";
import { useCallback, useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { uploadResume, UploadError } from "@/lib/upload-client";
import type { Resume, ResumeUploadResponse } from "@/features/resumes/types";
import { cn } from "@/lib/utils";

const MAX_SIZE_MB = 5;
const ACCEPT = "application/pdf";

type UploadState = "idle" | "dragging" | "uploading" | "success" | "error";

interface ResumeUploaderProps {
  replaceResume?: Resume | null;
  onSuccess?: (resume: ResumeUploadResponse) => void;
  onCancelReplace?: () => void;
}

export function ResumeUploader({
  replaceResume,
  onSuccess,
  onCancelReplace,
}: ResumeUploaderProps) {
  const { getToken } = useAuth();
  const inputRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<UploadState>("idle");
  const [progress, setProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const validateFile = (file: File): string | null => {
    if (file.type !== ACCEPT && !file.name.toLowerCase().endsWith(".pdf")) {
      return "Only PDF files are allowed";
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File must be under ${MAX_SIZE_MB} MB`;
    }
    return null;
  };

  const handleUpload = useCallback(
    async (file: File) => {
      const validationError = validateFile(file);
      if (validationError) {
        setState("error");
        setErrorMessage(validationError);
        toast.error(validationError);
        return;
      }

      setSelectedFile(file);
      setState("uploading");
      setProgress(0);
      setErrorMessage(null);

      try {
        const token = await getToken();
        if (!token) throw new Error("Not authenticated");

        const result = await uploadResume({
          file,
          token,
          title: file.name.replace(/\.pdf$/i, ""),
          replaceResumeId: replaceResume?.id,
          onProgress: setProgress,
        });

        setState("success");
        setProgress(100);
        toast.success(
          replaceResume ? "Resume replaced successfully" : "Resume uploaded successfully",
        );
        onSuccess?.(result.data as ResumeUploadResponse);
      } catch (err) {
        const message =
          err instanceof UploadError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Upload failed";
        setState("error");
        setErrorMessage(message);
        toast.error(message);
      }
    },
    [getToken, onSuccess, replaceResume?.id],
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setState("idle");
      const file = e.dataTransfer.files[0];
      if (file) void handleUpload(file);
    },
    [handleUpload],
  );

  const onFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) void handleUpload(file);
    e.target.value = "";
  };

  const reset = () => {
    setState("idle");
    setProgress(0);
    setErrorMessage(null);
    setSelectedFile(null);
  };

  return (
    <div className="space-y-4">
      {replaceResume && (
        <div className="flex items-center justify-between rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm">
          <span>
            Replacing: <strong>{replaceResume.file_name}</strong>
          </span>
          {onCancelReplace && (
            <Button variant="ghost" size="sm" onClick={onCancelReplace}>
              Cancel
            </Button>
          )}
        </div>
      )}

      <motion.div
        onDragOver={(e) => {
          e.preventDefault();
          setState("dragging");
        }}
        onDragLeave={() => setState("idle")}
        onDrop={onDrop}
        animate={{
          scale: state === "dragging" ? 1.01 : 1,
          borderColor:
            state === "dragging"
              ? "hsl(var(--primary))"
              : state === "success"
                ? "hsl(142 76% 36% / 0.5)"
                : state === "error"
                  ? "hsl(var(--destructive) / 0.5)"
                  : "hsl(var(--border))",
        }}
        className={cn(
          "relative overflow-hidden rounded-2xl border-2 border-dashed p-8 transition-colors md:p-12",
          state === "dragging" && "bg-primary/5",
          state === "uploading" && "pointer-events-none",
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT}
          className="hidden"
          onChange={onFileSelect}
        />

        <AnimatePresence mode="wait">
          {state === "uploading" && (
            <motion.div
              key="uploading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center text-center"
            >
              <Loader2 className="mb-4 h-12 w-12 animate-spin text-primary" />
              <p className="font-medium">Uploading{selectedFile ? ` ${selectedFile.name}` : ""}…</p>
              <div className="mt-6 w-full max-w-xs">
                <Progress value={progress} max={100} />
                <p className="mt-2 text-sm text-muted-foreground">{progress}%</p>
              </div>
            </motion.div>
          )}

          {state === "success" && (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center text-center"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
              >
                <CheckCircle2 className="mb-4 h-14 w-14 text-emerald-400" />
              </motion.div>
              <p className="text-lg font-semibold">Upload complete</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Your resume is saved and ready for analysis.
              </p>
              <Button variant="outline" className="mt-6" onClick={reset}>
                Upload another
              </Button>
            </motion.div>
          )}

          {state === "error" && (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center text-center"
            >
              <XCircle className="mb-4 h-12 w-12 text-destructive" />
              <p className="font-medium text-destructive">Upload failed</p>
              <p className="mt-1 text-sm text-muted-foreground">{errorMessage}</p>
              <Button className="mt-6" onClick={reset}>
                Try again
              </Button>
            </motion.div>
          )}

          {(state === "idle" || state === "dragging") && (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center text-center"
            >
              <div className="mb-4 rounded-2xl bg-primary/15 p-4">
                <Upload className="h-10 w-10 text-primary" />
              </div>
              <p className="text-lg font-semibold">
                {state === "dragging" ? "Drop your PDF here" : "Drag & drop your resume"}
              </p>
              <p className="mt-2 max-w-sm text-sm text-muted-foreground">
                PDF only · max {MAX_SIZE_MB} MB · secure validation on upload
              </p>
              <Button
                className="mt-6 gap-2"
                onClick={() => inputRef.current?.click()}
              >
                <FileUp className="h-4 w-4" />
                Browse files
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
