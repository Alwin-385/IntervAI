"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartCard } from "@/features/analytics/components/chart-card";
import type { WeakAreaFrequencyItem } from "@/features/analytics/types";

interface Props {
  data: WeakAreaFrequencyItem[];
}

export function WeakAreaFrequencyChart({ data }: Props) {
  const chartData = data.slice(0, 8).map((d) => ({
    name: d.area_name.length > 18 ? `${d.area_name.slice(0, 16)}…` : d.area_name,
    frequency: Math.round(d.frequency_rate * 100),
    count: d.frequency,
  }));

  return (
    <ChartCard title="Weak-area frequency" subtitle="How often each weakness appears in your history">
      <div className="h-64">
        {chartData.length === 0 ? (
          <p className="flex h-full items-center justify-center text-sm text-muted-foreground">
            No recurring weak areas detected yet.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }} />
              <YAxis
                type="category"
                dataKey="name"
                width={100}
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
              />
              <Tooltip
                formatter={(value: number, _name, props) => [
                  `${value}% (${(props.payload as { count: number }).count} hits)`,
                  "Frequency",
                ]}
                contentStyle={{
                  background: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: 8,
                }}
              />
              <Bar
                dataKey="frequency"
                fill="hsl(var(--primary))"
                radius={[0, 4, 4, 0]}
                animationDuration={800}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </ChartCard>
  );
}
