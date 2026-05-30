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

import type { StructuredSpeechAnalysis } from "@/features/speech/types";

interface SpeechAnalysisChartsProps {
  analysis: StructuredSpeechAnalysis;
  perQuestionScores?: { name: string; communication: number; fluency: number }[];
}

export function SpeechAnalysisCharts({ analysis, perQuestionScores }: SpeechAnalysisChartsProps) {
  const radarData = Object.entries(analysis.skill_radar).map(([subject, score]) => ({
    subject,
    score,
    fullMark: 100,
  }));

  const fillerData =
    analysis.filler_breakdown.length > 0
      ? analysis.filler_breakdown.map((f) => ({ word: f.word, count: f.count }))
      : [{ word: "none", count: 0 }];

  const confidenceData = Object.entries(analysis.confidence_indicators).map(([key, value]) => ({
    name: key.replace(/_/g, " "),
    value,
  }));

  const scoreBars = [
    { name: "Communication", value: analysis.scores.communication_score },
    { name: "Fluency", value: analysis.scores.fluency_score },
    { name: "Confidence", value: analysis.scores.confidence_score },
    { name: "Pace", value: analysis.scores.speaking_speed_score },
  ];

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="glass-card rounded-xl border border-border/50 p-4 lg:col-span-1">
        <h3 className="mb-3 text-sm font-semibold">Communication radar</h3>
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
        <h3 className="mb-3 text-sm font-semibold">Filler words</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={fillerData} margin={{ left: 4, right: 8, bottom: 4 }}>
              <XAxis dataKey="word" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
              <YAxis
                allowDecimals={false}
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              />
              <Tooltip />
              <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card rounded-xl border border-border/50 p-4 lg:col-span-1">
        <h3 className="mb-3 text-sm font-semibold">Score breakdown</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={scoreBars} layout="vertical" margin={{ left: 8, right: 16 }}>
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis
                type="category"
                dataKey="name"
                width={100}
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              />
              <Tooltip />
              <Bar dataKey="value" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {confidenceData.length > 0 && (
        <div className="glass-card rounded-xl border border-border/50 p-4 lg:col-span-3">
          <h3 className="mb-3 text-sm font-semibold">Confidence indicators</h3>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {confidenceData.map((row) => (
              <div key={row.name} className="space-y-1">
                <div className="flex justify-between text-xs capitalize text-muted-foreground">
                  <span>{row.name}</span>
                  <span className="font-medium text-foreground">{Math.round(row.value)}%</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-muted/50">
                  <div
                    className="h-full rounded-full bg-primary transition-all"
                    style={{ width: `${Math.min(100, row.value)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {perQuestionScores && perQuestionScores.length > 1 && (
        <div className="glass-card rounded-xl border border-border/50 p-4 lg:col-span-3">
          <h3 className="mb-3 text-sm font-semibold">Scores by question</h3>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={perQuestionScores}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar
                  dataKey="communication"
                  fill="hsl(var(--primary))"
                  name="Communication"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="fluency"
                  fill="hsl(220 70% 50%)"
                  name="Fluency"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
