"use client";

import {
  Bar,
  BarChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { StructuredAnswerEvaluation } from "@/features/evaluations/types";

interface AnswerEvaluationChartsProps {
  analysis: StructuredAnswerEvaluation;
  perQuestionScores?: { name: string; overall: number; technical: number }[];
}

export function AnswerEvaluationCharts({
  analysis,
  perQuestionScores,
}: AnswerEvaluationChartsProps) {
  const radarData = Object.entries(analysis.skill_radar).map(([subject, score]) => ({
    subject,
    score,
    fullMark: 100,
  }));

  const dimensionBars = [
    { name: "Relevance", value: analysis.scores.relevance_score },
    { name: "Clarity", value: analysis.scores.clarity_score },
    { name: "Tech accuracy", value: analysis.scores.technical_accuracy_score },
    { name: "Professionalism", value: analysis.scores.professionalism_score },
  ];

  const perQ =
    perQuestionScores && perQuestionScores.length > 1
      ? perQuestionScores.map((q) => ({
          name: q.name,
          overall: q.overall,
          technical: q.technical,
        }))
      : null;

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="glass-card rounded-xl border border-border/50 p-4 lg:col-span-1">
        <h3 className="mb-3 text-sm font-semibold">Answer quality radar</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid stroke="hsl(var(--border))" />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              />
              <Radar
                name="Score"
                dataKey="score"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary))"
                fillOpacity={0.35}
              />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card rounded-xl border border-border/50 p-4 lg:col-span-1">
        <h3 className="mb-3 text-sm font-semibold">Dimension scores</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dimensionBars} margin={{ left: 4, right: 8, bottom: 4 }}>
              <XAxis
                dataKey="name"
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                interval={0}
                angle={-20}
                textAnchor="end"
                height={50}
              />
              <YAxis domain={[0, 100]} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card rounded-xl border border-border/50 p-4 lg:col-span-1">
        <h3 className="mb-3 text-sm font-semibold">
          {perQ ? "Per-question scores" : "Core metrics"}
        </h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={
                perQ ?? [
                  { name: "Overall", overall: analysis.scores.overall_score, technical: 0 },
                  { name: "Comm.", overall: analysis.scores.communication_score, technical: 0 },
                  { name: "Complete", overall: analysis.scores.completeness_score, technical: 0 },
                ]
              }
              margin={{ left: 4, right: 8, bottom: 4 }}
            >
              <XAxis dataKey="name" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="overall" name="Overall" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              {perQ && (
                <Bar dataKey="technical" name="Technical" fill="hsl(var(--chart-2))" radius={[4, 4, 0, 0]} />
              )}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
