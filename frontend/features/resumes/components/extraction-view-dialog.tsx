"use client";

import { FileText } from "lucide-react";

import { Dialog } from "@/components/ui/dialog";
import { ExtractedDetails } from "@/features/resumes/components/extracted-details";
import type { Resume } from "@/features/resumes/types";

interface ExtractionViewDialogProps {
  resume: Resume;
  open: boolean;
  onClose: () => void;
}

export function ExtractionViewDialog({ resume, open, onClose }: ExtractionViewDialogProps) {
  const extracted = resume.extracted_data;
  const fullText = resume.cleaned_text ?? resume.content_text;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title={extracted?.name ?? resume.title}
      description={resume.file_name}
      className="max-w-4xl"
    >
      <div className="space-y-8">
        {extracted && (
          <section className="space-y-4">
            <h3 className="flex items-center gap-2 border-b border-border/50 pb-2 text-sm font-semibold">
              <FileText className="h-4 w-4 text-primary" />
              Structured extraction
            </h3>
            <ExtractedDetails data={extracted} />
          </section>
        )}

        {fullText && (
          <section className="space-y-3">
            <h3 className="border-b border-border/50 pb-2 text-sm font-semibold">
              Full cleaned text
            </h3>
            <div className="max-h-72 overflow-auto rounded-xl border border-border/50 bg-muted/15 p-4">
              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-foreground/85">
                {fullText}
              </pre>
            </div>
          </section>
        )}

        {resume.text_chunks && resume.text_chunks.length > 0 && (
          <p className="text-center text-xs text-muted-foreground">
            Indexed as {resume.text_chunks.length} chunks for AI search.
          </p>
        )}
      </div>
    </Dialog>
  );
}
