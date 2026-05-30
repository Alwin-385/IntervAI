"use client";

import type { LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

import { cn } from "@/lib/utils";

interface SelectionCardProps {
  icon: LucideIcon;
  label: string;
  blurb?: string;
  active: boolean;
  onSelect: () => void;
  accent?: string;
  disabled?: boolean;
}

export function SelectionCard({
  icon: Icon,
  label,
  blurb,
  active,
  onSelect,
  accent,
  disabled,
}: SelectionCardProps) {
  return (
    <motion.button
      type="button"
      whileHover={disabled ? undefined : { y: -2 }}
      whileTap={disabled ? undefined : { scale: 0.98 }}
      onClick={onSelect}
      disabled={disabled}
      className={cn(
        "group relative w-full overflow-hidden rounded-2xl border bg-card/60 p-5 text-left transition-all",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary",
        active
          ? "border-primary/70 bg-primary/10 shadow-lg shadow-primary/10 ring-1 ring-primary/40"
          : "border-border/60 hover:border-primary/40 hover:bg-card/80",
        disabled && "cursor-not-allowed opacity-50",
      )}
    >
      {accent && (
        <div
          aria-hidden
          className={cn(
            "absolute inset-x-0 -top-12 h-32 bg-gradient-to-b opacity-0 transition-opacity",
            accent,
            active ? "opacity-100" : "group-hover:opacity-60",
          )}
        />
      )}
      <div className="relative flex items-start gap-4">
        <div
          className={cn(
            "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors",
            active
              ? "bg-primary text-primary-foreground"
              : "bg-muted/50 text-foreground/80 group-hover:bg-primary/15 group-hover:text-primary",
          )}
        >
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-semibold leading-tight">{label}</p>
          {blurb && <p className="mt-1 text-xs text-muted-foreground">{blurb}</p>}
        </div>
      </div>
    </motion.button>
  );
}
