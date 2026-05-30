"use client";

import type { ExtractedResumeData } from "@/features/resumes/types";
import { contactEntries, hasExtractedContent } from "@/features/resumes/utils";

interface SectionProps {
  title: string;
  items: string[];
  compact?: boolean;
  maxItems?: number;
}

function FormattedEntry({ text, compact }: { text: string; compact?: boolean }) {
  const lines = text
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
  if (!lines.length) return null;

  const title = lines[0].replace(/^[-•]\s*/, "");
  const bullets = lines
    .slice(1)
    .map((l) => l.replace(/^[-•]\s*/, "").trim())
    .filter(Boolean);

  if (bullets.length === 0) {
    return (
      <p className={`text-sm leading-relaxed text-foreground/90 ${compact ? "line-clamp-3" : ""}`}>
        {title}
      </p>
    );
  }

  return (
    <div className="space-y-1.5">
      <p className="text-sm font-medium leading-snug text-foreground">{title}</p>
      <ul className={`space-y-1 text-sm text-foreground/85 ${compact ? "line-clamp-4" : ""}`}>
        {bullets.map((bullet, i) => (
          <li key={i} className="flex gap-2 leading-relaxed">
            <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary/80" aria-hidden />
            <span className="min-w-0 flex-1">{bullet}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function DetailSection({ title, items, compact, maxItems = 5 }: SectionProps) {
  if (!items.length) return null;
  const limit = compact ? Math.min(2, maxItems) : maxItems;
  const shown = items.slice(0, limit);
  return (
    <section className="min-w-0 rounded-xl border border-border/40 bg-muted/10 p-3.5">
      <h4 className="mb-3 text-xs font-semibold uppercase tracking-wide text-primary">{title}</h4>
      <div className="space-y-4">
        {shown.map((item, i) => (
          <div
            key={`${title}-${i}`}
            className={i > 0 ? "border-t border-border/30 pt-4" : undefined}
          >
            <FormattedEntry text={item} compact={compact} />
          </div>
        ))}
        {items.length > limit && (
          <p className="text-xs text-muted-foreground">+{items.length - limit} more entries</p>
        )}
      </div>
    </section>
  );
}

function ContactSection({
  contact,
  compact,
}: {
  contact: Record<string, string>;
  compact?: boolean;
}) {
  const entries = contactEntries(contact);
  if (!entries.length) return null;

  return (
    <section className="rounded-xl border border-primary/20 bg-primary/5 p-3.5 sm:col-span-2">
      <h4 className="mb-3 text-xs font-semibold uppercase tracking-wide text-primary">Contact</h4>
      <dl
        className={
          compact ? "grid gap-2 sm:grid-cols-2" : "grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
        }
      >
        {entries.map(([label, value]) => (
          <div
            key={label}
            className="rounded-lg border border-border/40 bg-background/60 px-3 py-2.5"
          >
            <dt className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              {label}
            </dt>
            <dd className="mt-1 break-all text-sm leading-snug text-foreground">{value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

interface ExtractedDetailsProps {
  data: ExtractedResumeData;
  compact?: boolean;
}

export function ExtractedDetails({ data, compact }: ExtractedDetailsProps) {
  if (!hasExtractedContent(data)) {
    return (
      <p className="text-xs text-muted-foreground">
        Extraction finished. No structured sections were detected — open full extraction for raw
        text.
      </p>
    );
  }

  const layoutClass = compact ? "grid grid-cols-1 gap-3 sm:grid-cols-2" : "flex flex-col gap-4";

  return (
    <div className={layoutClass}>
      <ContactSection contact={data.contact ?? {}} compact={compact} />
      <DetailSection title="Experience" items={data.experience} compact={compact} />
      <DetailSection title="Education" items={data.education} compact={compact} />
      <DetailSection title="Projects" items={data.projects} compact={compact} />
      {compact ? (
        <DetailSection title="Skills" items={data.skills} compact maxItems={6} />
      ) : (
        data.skills.length > 0 && (
          <section className="rounded-xl border border-border/40 bg-muted/10 p-3.5">
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wide text-primary">
              Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {data.skills.map((skill) => (
                <span
                  key={skill}
                  className="rounded-full border border-border/50 bg-background/80 px-2.5 py-1 text-xs text-foreground/90"
                >
                  {skill}
                </span>
              ))}
            </div>
          </section>
        )
      )}
      <DetailSection title="Internships" items={data.internships} compact={compact} />
      <DetailSection title="Certifications" items={data.certifications} compact={compact} />
      <DetailSection title="Achievements" items={data.achievements} compact={compact} />
    </div>
  );
}
