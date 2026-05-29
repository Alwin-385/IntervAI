"use client";

import type { ReactNode } from "react";
import { Briefcase, GraduationCap, Layers } from "lucide-react";

import { ContactChips } from "@/features/resumes/components/contact-chips";
import { Badge } from "@/components/ui/badge";
import type { ExtractedResumeData } from "@/features/resumes/types";
import { contactEntries } from "@/features/resumes/utils";

const SKILL_PREVIEW = 5;

function entryHeadline(text: string, maxLen = 110): string {
  const line = text.split("\n").map((l) => l.trim()).find(Boolean) ?? "";
  const headline = line.replace(/^[-•]\s*/, "").trim();
  if (headline.length <= maxLen) return headline;
  return `${headline.slice(0, maxLen).trim()}…`;
}

interface GlanceRowProps {
  icon: ReactNode;
  label: string;
  value: string;
}

function GlanceRow({ icon, label, value }: GlanceRowProps) {
  return (
    <div className="flex gap-2.5 rounded-lg border border-border/40 bg-background/40 px-3 py-2">
      <div className="mt-0.5 shrink-0 text-primary/80">{icon}</div>
      <div className="min-w-0 flex-1">
        <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
          {label}
        </p>
        <p className="mt-0.5 text-sm leading-snug text-foreground" title={value}>
          {value}
        </p>
      </div>
    </div>
  );
}

interface ResumeCardSummaryProps {
  data: ExtractedResumeData;
}

export function ResumeCardSummary({ data }: ResumeCardSummaryProps) {
  const contactCount = contactEntries(data.contact).length;
  const experience = data.experience[0] ? entryHeadline(data.experience[0]) : null;
  const education = data.education[0] ? entryHeadline(data.education[0]) : null;
  const project = data.projects[0] ? entryHeadline(data.projects[0]) : null;

  const extraSections = [
    data.experience.length > 1,
    data.education.length > 1,
    data.projects.length > 1,
    data.internships.length > 0,
    data.certifications.length > 0,
    data.achievements.length > 0,
  ].filter(Boolean).length;

  const hasGlance = experience || education || project;

  return (
    <div className="space-y-3 rounded-lg border border-border/40 bg-muted/10 p-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Profile summary
      </p>

      {contactCount > 0 && <ContactChips contact={data.contact} />}

      {data.skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {data.skills.slice(0, SKILL_PREVIEW).map((skill) => (
            <Badge key={skill} variant="outline" className="text-xs font-normal">
              {skill}
            </Badge>
          ))}
          {data.skills.length > SKILL_PREVIEW && (
            <Badge variant="outline" className="text-xs font-normal">
              +{data.skills.length - SKILL_PREVIEW} skills
            </Badge>
          )}
        </div>
      )}

      {hasGlance && (
        <div className="space-y-2">
          {experience && (
            <GlanceRow
              icon={<Briefcase className="h-3.5 w-3.5" />}
              label="Latest experience"
              value={experience}
            />
          )}
          {education && (
            <GlanceRow
              icon={<GraduationCap className="h-3.5 w-3.5" />}
              label="Education"
              value={education}
            />
          )}
          {project && (
            <GlanceRow
              icon={<Layers className="h-3.5 w-3.5" />}
              label="Top project"
              value={project}
            />
          )}
        </div>
      )}

      <p className="text-xs text-muted-foreground">
        {extraSections > 0
          ? `${extraSections} more section${extraSections === 1 ? "" : "s"} in full extraction.`
          : "Use View full extraction for the complete structured profile."}
      </p>
    </div>
  );
}
