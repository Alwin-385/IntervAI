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

import type { ATSBreakdown, StructuredResumeAnalysis } from "@/features/resume-analysis/types";

interface AnalysisChartsProps {
  analysis: StructuredResumeAnalysis;
}

export function AnalysisCharts({ analysis }: AnalysisChartsProps) {
  const radarData = Object.entries(analysis.skill_radar).map(([subject, score]) => ({
    subject,
    score,
    fullMark: 100,
  }));

  const atsData = atsBreakdownRows(analysis.ats_breakdown);
  const readinessRows = [
    { name: "Role readiness", value: analysis.scores.role_readiness_score },
    { name: "Technical", value: analysis.scores.technical_skill_score },
    { name: "Projects", value: analysis.scores.project_strength_score },
    { name: "Communication", value: analysis.scores.communication_score },
  ];

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="glass-card rounded-xl border border-border/50 p-4 lg:col-span-1">
        <h3 className="mb-3 text-sm font-semibold">Skill radar</h3>
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
        <h3 className="mb-3 text-sm font-semibold">ATS breakdown</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={atsData} layout="vertical" margin={{ left: 8, right: 16 }}>
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis
                type="category"
                dataKey="name"
                width={110}
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              />
              <Tooltip />
              <Bar dataKey="value" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card rounded-xl border border-border/50 p-4 lg:col-span-1">
        <h3 className="mb-3 text-sm font-semibold">Readiness bars</h3>
        <div className="space-y-4 pt-2">
          {readinessRows.map((row) => (
            <div key={row.name}>
              <div className="mb-1 flex justify-between text-xs">
                <span className="text-muted-foreground">{row.name}</span>
                <span className="font-medium">{Math.round(row.value)}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-primary to-accent transition-all duration-700"
                  style={{ width: `${row.value}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function atsBreakdownRows(breakdown: ATSBreakdown) {
  return [
    { name: "Keywords", value: breakdown.keyword_match },
    { name: "Formatting", value: breakdown.formatting },
    { name: "Sections", value: breakdown.section_completeness },
    { name: "Contact", value: breakdown.contact_info },
  ];
}
