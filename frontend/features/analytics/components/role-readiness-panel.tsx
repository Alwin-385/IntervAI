"use client";

import { Progress } from "@/components/ui/progress";
import { ChartCard } from "@/features/analytics/components/chart-card";
import type { RoleReadinessItem } from "@/features/analytics/types";

interface Props {
  items: RoleReadinessItem[];
}

export function RoleReadinessPanel({ items }: Props) {
  return (
    <ChartCard title="Role readiness" subtitle="Composite readiness by target role">
      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground py-6 text-center">
          Complete interviews for different roles to see readiness scores.
        </p>
      ) : (
        <ul className="space-y-4">
          {items.map((item) => (
            <li key={item.target_role}>
              <div className="flex items-center justify-between text-sm mb-1.5">
                <span className="font-medium">{item.target_role}</span>
                <span className="text-muted-foreground">
                  {item.readiness_score}% · {item.interviews_completed} interview(s)
                </span>
              </div>
              <Progress value={item.readiness_score} className="h-2" />
              <p className="mt-1 text-xs text-muted-foreground capitalize">
                Trend: {item.trend.replace(/_/g, " ")}
                {item.average_score != null ? ` · Avg ${item.average_score}%` : ""}
              </p>
            </li>
          ))}
        </ul>
      )}
    </ChartCard>
  );
}
