"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Activity, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchHealth } from "@/features/health/api";
import { env } from "@/lib/env";
import { logger } from "@/lib/logger";

export function HealthStatus() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      logger.info("Fetching backend health", { url: env.apiUrl });
      return fetchHealth();
    },
    retry: 2,
  });

  return (
    <Card className="border-border/60 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Activity className="h-5 w-5 text-primary" />
          API Connection
        </CardTitle>
        <CardDescription>
          Live status from{" "}
          <code className="rounded bg-muted px-1.5 py-0.5 text-xs">{env.apiUrl}/api/v1/health</code>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading && (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Connecting to backend…
          </div>
        )}

        {isError && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col gap-3"
          >
            <div className="flex items-start gap-2 text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span className="text-sm">{(error as Error)?.message ?? "Backend unreachable"}</span>
            </div>
            <button
              type="button"
              onClick={() => refetch()}
              className="text-sm text-primary hover:underline"
            >
              Retry connection
            </button>
          </motion.div>
        )}

        {data && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3"
          >
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="success" className="gap-1">
                <CheckCircle2 className="h-3 w-3" />
                {data.status}
              </Badge>
              <Badge variant="secondary">{data.environment}</Badge>
              <Badge variant="outline">v{data.version}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{data.service}</p>
          </motion.div>
        )}

        {isFetching && !isLoading && <p className="text-xs text-muted-foreground">Refreshing…</p>}
      </CardContent>
    </Card>
  );
}
