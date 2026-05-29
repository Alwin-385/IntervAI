"use client";

import { contactEntries } from "@/features/resumes/utils";

interface ContactChipsProps {
  contact: Record<string, string> | undefined;
}

export function ContactChips({ contact }: ContactChipsProps) {
  const entries = contactEntries(contact);
  if (!entries.length) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {entries.map(([label, value]) => (
        <div
          key={label}
          className="max-w-full rounded-lg border border-border/50 bg-muted/20 px-2.5 py-1.5 text-xs"
        >
          <span className="font-semibold text-primary/90">{label}: </span>
          <span className="break-all text-foreground/90" title={value}>
            {value.length > 48 ? `${value.slice(0, 48)}…` : value}
          </span>
        </div>
      ))}
    </div>
  );
}
