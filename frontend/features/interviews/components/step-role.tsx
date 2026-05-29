"use client";

import { useEffect, useState } from "react";

import { Input } from "@/components/ui/input";
import { PRESET_ROLES } from "@/features/interviews/constants";
import { SelectionCard } from "@/features/interviews/components/selection-card";

interface StepRoleProps {
  value: string;
  custom: boolean;
  onChange: (role: string, custom: boolean) => void;
}

export function StepRole({ value, custom, onChange }: StepRoleProps) {
  const [customDraft, setCustomDraft] = useState(custom ? value : "");

  useEffect(() => {
    if (!custom) setCustomDraft("");
  }, [custom]);

  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-xl font-semibold">Which role are you preparing for?</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Questions, vocabulary, and difficulty calibration adjust to the role you pick.
        </p>
      </header>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {PRESET_ROLES.map((role) => {
          const isCustom = !!role.custom;
          const active = isCustom ? custom : !custom && value === role.value;
          return (
            <SelectionCard
              key={role.label}
              icon={role.icon}
              label={role.label}
              blurb={role.blurb}
              active={active}
              onSelect={() => {
                if (isCustom) {
                  onChange(customDraft, true);
                } else {
                  onChange(role.value, false);
                }
              }}
            />
          );
        })}
      </div>

      {custom && (
        <div className="rounded-xl border border-border/60 bg-card/60 p-4">
          <label
            htmlFor="custom-role"
            className="mb-1.5 block text-xs font-medium text-muted-foreground"
          >
            Custom role
          </label>
          <Input
            id="custom-role"
            value={customDraft}
            placeholder="e.g. Solidity Engineer, Solutions Architect"
            onChange={(e) => {
              setCustomDraft(e.target.value);
              onChange(e.target.value, true);
            }}
            autoFocus
            maxLength={120}
          />
        </div>
      )}
    </div>
  );
}
