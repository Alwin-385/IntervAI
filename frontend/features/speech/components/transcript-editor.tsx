"use client";

import { Pencil } from "lucide-react";

interface TranscriptEditorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function TranscriptEditor({
  value,
  onChange,
  disabled = false,
  placeholder = "Your transcript will appear here. You can edit it before submitting.",
}: TranscriptEditorProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        <Pencil className="h-3.5 w-3.5" />
        Transcript
      </div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder}
        className="min-h-[140px] w-full resize-y rounded-xl border border-input bg-background/70 p-4 text-sm leading-relaxed outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-60"
      />
      <p className="text-[11px] text-muted-foreground">
        Edit the transcript if needed — your final answer uses this text.
      </p>
    </div>
  );
}
