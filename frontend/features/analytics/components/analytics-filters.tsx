"use client";

import { Button } from "@/components/ui/button";

export interface AnalyticsFilterState {
  target_role?: string;
  category?: string;
  days?: number;
  page: number;
}

interface Props {
  filters: AnalyticsFilterState;
  availableRoles: string[];
  availableCategories: string[];
  onChange: (next: Partial<AnalyticsFilterState>) => void;
}

const DAY_OPTIONS = [
  { label: "All time", value: undefined },
  { label: "30 days", value: 30 },
  { label: "90 days", value: 90 },
  { label: "180 days", value: 180 },
];

const CATEGORY_LABELS: Record<string, string> = {
  hr: "HR",
  technical: "Technical",
  behavioral: "Behavioral",
  dsa: "DSA",
  resume_based: "Resume-based",
  mixed: "Mixed",
};

export function AnalyticsFilters({
  filters,
  availableRoles,
  availableCategories,
  onChange,
}: Props) {
  return (
    <div className="glass-card rounded-xl border border-border/50 p-4 space-y-4">
      <p className="text-sm font-semibold">Filters</p>

      <div className="flex flex-wrap gap-2">
        <span className="w-full text-xs text-muted-foreground">Time range</span>
        {DAY_OPTIONS.map((opt) => (
          <Button
            key={opt.label}
            size="sm"
            variant={filters.days === opt.value ? "default" : "outline"}
            onClick={() => onChange({ days: opt.value, page: 1 })}
          >
            {opt.label}
          </Button>
        ))}
      </div>

      {availableRoles.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <span className="w-full text-xs text-muted-foreground">Target role</span>
          <Button
            size="sm"
            variant={!filters.target_role ? "default" : "outline"}
            onClick={() => onChange({ target_role: undefined, page: 1 })}
          >
            All roles
          </Button>
          {availableRoles.map((role) => (
            <Button
              key={role}
              size="sm"
              variant={filters.target_role === role ? "default" : "outline"}
              onClick={() => onChange({ target_role: role, page: 1 })}
            >
              {role}
            </Button>
          ))}
        </div>
      )}

      {availableCategories.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <span className="w-full text-xs text-muted-foreground">Interview type</span>
          <Button
            size="sm"
            variant={!filters.category ? "default" : "outline"}
            onClick={() => onChange({ category: undefined, page: 1 })}
          >
            All types
          </Button>
          {availableCategories.map((cat) => (
            <Button
              key={cat}
              size="sm"
              variant={filters.category === cat ? "default" : "outline"}
              onClick={() => onChange({ category: cat, page: 1 })}
            >
              {CATEGORY_LABELS[cat] ?? cat}
            </Button>
          ))}
        </div>
      )}
    </div>
  );
}
