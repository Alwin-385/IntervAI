"use client";

import { motion } from "framer-motion";
import { Clock, Inbox } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const placeholders = [
  { title: "No interviews yet", time: "—" },
  { title: "No resume uploads", time: "—" },
  { title: "No evaluations", time: "—" },
];

interface RecentActivityProps {
  isLoading?: boolean;
}

export function RecentActivity({ isLoading }: RecentActivityProps) {
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
        ) : (
          <div className="space-y-1">
            {placeholders.map((item, index) => (
              <motion.div
                key={item.title}
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
                    {item.title}
                  </p>
                  <p className="text-xs text-muted-foreground/70">{item.time}</p>
                </div>
              </motion.div>
            ))}
            <p className="pt-4 text-center text-xs text-muted-foreground">
              Activity will populate after your first interview session
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
