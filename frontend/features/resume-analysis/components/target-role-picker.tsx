"use client";

import { useMemo, useState } from "react";
import { Briefcase } from "lucide-react";

import { Input } from "@/components/ui/input";
import { POPULAR_TARGET_ROLES } from "@/features/resume-analysis/constants";

interface TargetRolePickerProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function TargetRolePicker({ value, onChange, disabled }: TargetRolePickerProps) {
  const [focused, setFocused] = useState(false);
  const listId = "target-role-suggestions";

  const suggestions = useMemo(() => {
    const q = value.trim().toLowerCase();
    if (!q) return [...POPULAR_TARGET_ROLES];
    return POPULAR_TARGET_ROLES.filter((role) => role.toLowerCase().includes(q));
  }, [value]);

  return (
    <div className="w-full min-w-[220px] max-w-md">
      <label
        className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground"
        htmlFor="target-role"
      >
        <Briefcase className="h-3 w-3" />
        Target role
      </label>
      <Input
        id="target-role"
        list={listId}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setTimeout(() => setFocused(false), 200)}
        placeholder="Type or pick a role…"
        autoComplete="off"
      />
      <datalist id={listId}>
        {POPULAR_TARGET_ROLES.map((role) => (
          <option key={role} value={role} />
        ))}
      </datalist>

      {focused && suggestions.length > 0 && (
        <div className="mt-2 rounded-lg border border-border/60 bg-card/95 p-2.5 shadow-sm">
          <p className="mb-2 px-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
            Popular roles
          </p>
          <div className="flex max-h-32 flex-wrap gap-1.5 overflow-y-auto">
            {suggestions.map((role) => (
              <button
                key={role}
                type="button"
                disabled={disabled}
                className="rounded-md border border-border/50 bg-muted/30 px-2.5 py-1 text-xs transition-colors hover:border-primary/40 hover:bg-primary/10 hover:text-primary"
                onMouseDown={(e) => {
                  e.preventDefault();
                  onChange(role);
                  setFocused(false);
                }}
              >
                {role}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
