"use client";

import { motion } from "framer-motion";
import {
  BarChart3,
  Calendar,
  FileText,
  Mic,
  TrendingUp,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useBackendUser } from "@/hooks/use-backend-user";

const stats = [
  { label: "Mock interviews", value: "0", icon: Mic, change: "Start your first" },
  { label: "Resumes", value: "0", icon: FileText, change: "Upload to analyze" },
  { label: "Avg. score", value: "—", icon: TrendingUp, change: "No data yet" },
  { label: "This week", value: "0h", icon: Calendar, change: "Practice time" },
];

export default function DashboardPage() {
  const { data: user, isLoading, isError, error } = useBackendUser();

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <Badge variant="secondary" className="mb-3">
          Dashboard
        </Badge>
        <h1 className="text-3xl font-bold tracking-tight">
          {isLoading
            ? "Loading your workspace…"
            : `Welcome back${user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}`}
        </h1>
        <p className="mt-2 text-muted-foreground">
          Track interviews, resumes, and skill growth in one place.
        </p>
        {isError && (
          <p className="mt-2 text-sm text-destructive">
            {(error as Error).message}
          </p>
        )}
        {user && (
          <p className="mt-1 text-xs text-muted-foreground">
            Synced account · {user.email}
          </p>
        )}
      </motion.div>

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <Card className="border-border/60 bg-card/80">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <stat.icon className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">{stat.change}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-8 grid gap-6 lg:grid-cols-2"
      >
        <Card className="border-border/60 bg-card/80">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" />
              Performance overview
            </CardTitle>
            <CardDescription>
              Your interview scores will appear here after your first session.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-border/80 bg-muted/20 text-sm text-muted-foreground">
              Chart placeholder — Recharts in a future phase
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/80">
          <CardHeader>
            <CardTitle>Quick actions</CardTitle>
            <CardDescription>Jump into your interview prep workflow</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>• Upload a resume for AI analysis</p>
            <p>• Start a mock interview session</p>
            <p>• Review weak areas and roadmaps</p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
