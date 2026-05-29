"use client";

import type { ReactNode } from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  BookOpen,
  Code2,
  Lightbulb,
  MessageSquareQuote,
  Sparkles,
  Star,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { StructuredAnswerEvaluation } from "@/features/evaluations/types";

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

interface AnswerEvaluationSectionsProps {
  analysis: StructuredAnswerEvaluation;
}

export function AnswerEvaluationSections({ analysis }: AnswerEvaluationSectionsProps) {
  return (
    <div className="space-y-6">
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="rounded-xl border border-border/50 bg-muted/15 p-4 text-sm leading-relaxed text-foreground/90"
      >
        <MessageSquareQuote className="mb-2 h-4 w-4 text-primary" />
        {analysis.summary_feedback}
      </motion.p>

      {!analysis.is_correct && (analysis.correct_answer || analysis.reference_answer) && (
        <SectionCard
          title="Correct answer"
          icon={<BookOpen className="h-4 w-4 text-emerald-500" />}
          delay={0.05}
        >
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
            {analysis.correct_answer || analysis.reference_answer}
          </p>
        </SectionCard>
      )}

      {analysis.rubric_points_matched.length > 0 && (
        <SectionCard
          title="What you got right"
          icon={<Sparkles className="h-4 w-4 text-emerald-500" />}
          delay={0.08}
        >
          <ul className="space-y-2 text-sm">
            {analysis.rubric_points_matched.map((p) => (
              <li key={p} className="rounded-md bg-emerald-500/10 px-3 py-2">
                {p}
              </li>
            ))}
          </ul>
        </SectionCard>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <SectionCard
          title="Strengths"
          icon={<Sparkles className="h-4 w-4 text-emerald-500" />}
          delay={0.1}
        >
          <ul className="space-y-2 text-sm text-foreground/90">
            {analysis.strengths.map((item) => (
              <li key={item} className="rounded-md bg-emerald-500/10 px-3 py-2 leading-snug">
                {item}
              </li>
            ))}
          </ul>
        </SectionCard>

        <SectionCard
          title="Weaknesses"
          icon={<AlertTriangle className="h-4 w-4 text-amber-500" />}
          delay={0.15}
        >
          <ul className="space-y-2 text-sm text-foreground/90">
            {analysis.weaknesses.map((item) => (
              <li key={item} className="rounded-md bg-amber-500/10 px-3 py-2 leading-snug">
                {item}
              </li>
            ))}
          </ul>
        </SectionCard>
      </div>

      {analysis.missing_concepts.length > 0 && (
        <SectionCard
          title="Missing concepts"
          icon={<BookOpen className="h-4 w-4 text-primary" />}
          delay={0.2}
        >
          <div className="flex flex-wrap gap-2">
            {analysis.missing_concepts.map((c) => (
              <Badge key={c} variant="outline" className="font-normal">
                {c}
              </Badge>
            ))}
          </div>
        </SectionCard>
      )}

      {analysis.technical_feedback && (
        <SectionCard
          title="Technical feedback"
          icon={<Code2 className="h-4 w-4 text-primary" />}
          delay={0.25}
        >
          <p className="text-sm leading-relaxed text-foreground/90">{analysis.technical_feedback}</p>
        </SectionCard>
      )}

      {analysis.star_feedback && (
        <SectionCard
          title="STAR method analysis"
          icon={<Star className="h-4 w-4 text-primary" />}
          delay={0.3}
        >
          <div className="mb-4 grid gap-2 sm:grid-cols-4">
            {(
              [
                ["Situation", analysis.star_feedback.situation_score],
                ["Task", analysis.star_feedback.task_score],
                ["Action", analysis.star_feedback.action_score],
                ["Result", analysis.star_feedback.result_score],
              ] as const
            ).map(([label, score]) => (
              <div key={label} className="rounded-md bg-muted/20 px-3 py-2 text-center">
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="text-lg font-bold tabular-nums">{Math.round(score)}%</p>
              </div>
            ))}
          </div>
          <p className="text-sm leading-relaxed text-foreground/90">{analysis.star_feedback.feedback}</p>
          {analysis.star_feedback.missing_elements.length > 0 && (
            <ul className="mt-3 space-y-1 text-sm text-muted-foreground">
              {analysis.star_feedback.missing_elements.map((el) => (
                <li key={el}>• {el}</li>
              ))}
            </ul>
          )}
          {analysis.star_feedback.improved_star_outline && (
            <p className="mt-3 rounded-md bg-primary/5 px-3 py-2 text-sm italic">
              {analysis.star_feedback.improved_star_outline}
            </p>
          )}
        </SectionCard>
      )}

      {analysis.dsa_feedback && (
        <SectionCard
          title="DSA complexity analysis"
          icon={<Code2 className="h-4 w-4 text-violet-500" />}
          delay={0.35}
        >
          <div className="mb-3 flex flex-wrap gap-2">
            <Badge variant="secondary">Time: {analysis.dsa_feedback.time_complexity}</Badge>
            <Badge variant="secondary">Space: {analysis.dsa_feedback.space_complexity}</Badge>
            <Badge variant="outline">
              Correctness {Math.round(analysis.dsa_feedback.correctness_score)}%
            </Badge>
            <Badge variant="outline">
              Optimality {Math.round(analysis.dsa_feedback.optimality_score)}%
            </Badge>
          </div>
          <p className="text-sm leading-relaxed text-foreground/90">{analysis.dsa_feedback.feedback}</p>
          {analysis.dsa_feedback.suggested_improvements.length > 0 && (
            <ul className="mt-3 space-y-2 text-sm">
              {analysis.dsa_feedback.suggested_improvements.map((tip) => (
                <li key={tip} className="rounded-md bg-muted/20 px-3 py-2">
                  {tip}
                </li>
              ))}
            </ul>
          )}
        </SectionCard>
      )}

      {analysis.improved_answer && (
        <SectionCard
          title="Improved sample answer"
          icon={<MessageSquareQuote className="h-4 w-4 text-primary" />}
          delay={0.4}
        >
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
            {analysis.improved_answer}
          </p>
        </SectionCard>
      )}

      <SectionCard
        title="Improvement suggestions"
        icon={<Lightbulb className="h-4 w-4 text-amber-400" />}
        delay={0.45}
      >
        <ul className="space-y-2 text-sm text-foreground/90">
          {analysis.improvement_suggestions.map((item) => (
            <li key={item} className="rounded-md bg-muted/20 px-3 py-2 leading-snug">
              {item}
            </li>
          ))}
        </ul>
      </SectionCard>
    </div>
  );
}
