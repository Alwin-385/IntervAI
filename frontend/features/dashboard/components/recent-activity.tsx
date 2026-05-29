"use client";

import { motion } from "framer-motion";
import {
  AlertCircle,
  Clock,
  FileCheck,
  FileText,
  Inbox,
  Loader2,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { DashboardActivityItem } from "@/features/dashboard/types";

function activityIcon(kind: string) {
  switch (kind) {
    case "resume_analyzed":
      return FileCheck;
    case "resume_processing":
      return Loader2;
    case "resume_failed":
      return AlertCircle;
    case "resume_upload":
    default:
      return FileText;
  }
}

function formatWhen(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

interface RecentActivityProps {
  items?: DashboardActivityItem[];
  isLoading?: boolean;
}

export function RecentActivity({ items = [], isLoading }: RecentActivityProps) {
  const hasItems = items.length > 0;

  return (
    <Card className="glass-card border-border/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-primary" />
          Recent activity
        </CardTitle>
        <CardDescription>Your latest sessions and uploads</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex gap-3">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/4" />
                </div>
              </div>
            ))}
          </div>
        ) : hasItems ? (
          <div className="space-y-2">
            {items.map((item, index) => {
              const Icon = activityIcon(item.kind);
              const spinning = item.kind === "resume_processing";
              return (
                <motion.div
                  key={`${item.kind}-${item.timestamp}-${index}`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.04 }}
                  className="flex items-start gap-4 rounded-lg border border-border/50 bg-muted/10 px-4 py-3"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <Icon
                      className={`h-4 w-4 text-primary ${spinning ? "animate-spin" : ""}`}
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium leading-snug">{item.title}</p>
                    <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">
                      {item.subtitle}
                    </p>
                    <p className="mt-1 text-[11px] text-muted-foreground/80">
                      {formatWhen(item.timestamp)}
                    </p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        ) : (
          <div className="space-y-1">
            {[
              { title: "No interviews yet", time: "—" },
              { title: "No resume uploads", time: "—" },
              { title: "No evaluations", time: "—" },
            ].map((placeholder, index) => (
              <motion.div
                key={placeholder.title}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-4 rounded-lg border border-dashed border-border/60 px-4 py-4"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted/50">
                  <Inbox className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-muted-foreground">
                    {placeholder.title}
                  </p>
                  <p className="text-xs text-muted-foreground/70">{placeholder.time}</p>
                </div>
              </motion.div>
            ))}
            <p className="pt-4 text-center text-xs text-muted-foreground">
              Upload a resume or start an interview to see activity here
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
