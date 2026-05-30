"use client";

import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Lightbulb, MessageSquareQuote, Target } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { StructuredResumeAnalysis } from "@/features/resume-analysis/types";

interface AnalysisSectionsProps {
  analysis: StructuredResumeAnalysis;
}

function SectionCard({
  title,
  icon,
  children,
  delay,
}: {
  title: string;
  icon: ReactNode;
  children: React.ReactNode;
  delay: number;
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="glass-card rounded-xl border border-border/50 p-5"
    >
      <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold">
        {icon}
        {title}
      </h3>
      {children}
    </motion.section>
  );
}

export function AnalysisSections({ analysis }: AnalysisSectionsProps) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-2">
        <SectionCard
          title="Profile snapshot"
          icon={<Target className="h-4 w-4 text-primary" />}
          delay={0.1}
        >
          <div className="space-y-4">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Skills</p>
              <div className="flex flex-wrap gap-1.5">
                {analysis.extracted_skills.slice(0, 20).map((s) => (
                  <Badge key={s} variant="outline" className="text-xs font-normal">
                    {s}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
                Technologies
              </p>
              <div className="flex flex-wrap gap-1.5">
                {analysis.technologies.map((t) => (
                  <Badge key={t} variant="secondary" className="text-xs font-normal">
                    {t}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
                Experience summary
              </p>
              <ul className="space-y-2 text-sm text-foreground/90">
                {analysis.experience_summary.map((item, i) => (
                  <li key={i} className="rounded-md bg-muted/20 px-3 py-2 leading-snug">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Projects</p>
              <ul className="space-y-2 text-sm text-foreground/90">
                {analysis.projects_summary.map((item, i) => (
                  <li key={i} className="rounded-md bg-muted/20 px-3 py-2 leading-snug">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Recruiter feedback"
          icon={<MessageSquareQuote className="h-4 w-4 text-primary" />}
          delay={0.15}
        >
          <p className="text-sm leading-relaxed text-foreground/90">
            {analysis.recruiter_feedback}
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div>
              <p className="mb-2 text-xs font-semibold text-emerald-400">Strengths</p>
              <ul className="space-y-1.5 text-sm">
                {analysis.strengths.map((s, i) => (
                  <li key={i} className="text-foreground/85">
                    • {s}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold text-amber-400">Weak areas</p>
              <ul className="space-y-1.5 text-sm">
                {analysis.weaknesses.map((w, i) => (
                  <li key={i} className="text-foreground/85">
                    • {w}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </SectionCard>
      </div>

      <SectionCard
        title="Improvement plan"
        icon={<Lightbulb className="h-4 w-4 text-primary" />}
        delay={0.2}
      >
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
              Missing keywords
            </p>
            <div className="flex flex-wrap gap-1.5">
              {analysis.missing_keywords.map((k) => (
                <Badge key={k} variant="outline" className="border-amber-500/30 text-amber-200">
                  {k}
                </Badge>
              ))}
            </div>
          </div>
          <div>
            <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
              Missing technologies
            </p>
            <div className="flex flex-wrap gap-1.5">
              {analysis.missing_technologies.map((t) => (
                <Badge key={t} variant="outline" className="border-amber-500/30 text-amber-200">
                  {t}
                </Badge>
              ))}
            </div>
          </div>
        </div>
        <div className="mt-4">
          <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase text-muted-foreground">
            <AlertTriangle className="h-3.5 w-3.5" />
            Formatting issues
          </p>
          <ul className="space-y-1 text-sm text-muted-foreground">
            {analysis.formatting_issues.length > 0 ? (
              analysis.formatting_issues.map((issue, i) => <li key={i}>• {issue}</li>)
            ) : (
              <li>No major formatting issues flagged.</li>
            )}
          </ul>
        </div>
        <div className="mt-4">
          <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
            Recommendations
          </p>
          <ul className="space-y-2 text-sm">
            {analysis.recommendations.map((r, i) => (
              <li key={i} className="rounded-lg border border-border/40 bg-muted/15 px-3 py-2">
                {r}
              </li>
            ))}
          </ul>
        </div>
        <div className="mt-4">
          <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
            Suggested interview topics
          </p>
          <div className="flex flex-wrap gap-2">
            {analysis.interview_topics.map((topic) => (
              <Badge key={topic} className="bg-primary/15 text-primary">
                {topic}
              </Badge>
            ))}
          </div>
        </div>
      </SectionCard>
    </div>
  );
}
