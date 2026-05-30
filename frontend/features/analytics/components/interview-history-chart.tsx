"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ChartCard } from "@/features/analytics/components/chart-card";
import type { InterviewHistoryItem } from "@/features/analytics/types";

interface Props {
  history: InterviewHistoryItem[];
}

export function InterviewHistoryChart({ history }: Props) {
  const chartData = [...history]
    .reverse()
    .slice(-12)
    .map((h) => ({
      name: h.title.length > 12 ? `${h.title.slice(0, 10)}…` : h.title,
      score: h.average_score ?? 0,
      communication: h.communication_score ?? 0,
    }));

  return (
    <ChartCard title="Interview history" subtitle="Scores across your recent sessions">
      <div className="h-64">
        {chartData.length === 0 ? (
          <p className="flex h-full items-center justify-center text-sm text-muted-foreground">
            No completed interviews in this filter range.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 8, right: 8, left: -8, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="name" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }} />
              <YAxis
                domain={[0, 100]}
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
              />
              <Tooltip
                contentStyle={{
                  background: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: 8,
                }}
              />
              <Bar
                dataKey="score"
                name="Overall"
                fill="hsl(var(--primary))"
                radius={[4, 4, 0, 0]}
                animationDuration={800}
              />
              <Bar
                dataKey="communication"
                name="Communication"
                fill="hsl(var(--accent))"
                radius={[4, 4, 0, 0]}
                animationDuration={800}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </ChartCard>
  );
}
