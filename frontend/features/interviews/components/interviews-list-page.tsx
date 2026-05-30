"use client";

import Link from "next/link";
import { Mic, Plus, Sparkles, Trash2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { DeleteInterviewDialog } from "@/features/interviews/components/delete-interview-dialog";
import { useInterviewSessions } from "@/features/interviews/hooks/use-interview-sessions";
import {
  answerModeLabel,
  categoryLabel,
  difficultyLabel,
  statusLabel,
  statusTone,
} from "@/features/interviews/utils";

export function InterviewsListPage() {
  const { data, isLoading } = useInterviewSessions(1, 20);
  const sessions = data?.items ?? [];

  return (
    <div className="space-y-6 p-4 md:p-8">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 text-primary">
            <Mic className="h-5 w-5" />
            <span className="text-sm font-medium">Interviews</span>
          </div>
          <h1 className="mt-1 text-2xl font-bold tracking-tight">Mock interview sessions</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Set up role-targeted interviews with custom difficulty and question count.
          </p>
        </div>
        <Button asChild className="gap-2">
          <Link href="/dashboard/interviews/new">
            <Plus className="h-4 w-4" />
            New interview
          </Link>
        </Button>
      </header>

      {isLoading && (
        <div className="grid gap-3 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-xl" />
          ))}
        </div>
      )}

      {!isLoading && sessions.length === 0 && (
        <Card className="glass-card border-dashed border-primary/30 bg-primary/5">
          <CardContent className="flex flex-col items-center justify-center gap-3 py-16 text-center">
            <Sparkles className="h-10 w-10 text-primary" />
            <p className="text-lg font-medium">No interviews yet</p>
            <p className="max-w-md text-sm text-muted-foreground">
              Start your first mock interview. Pick a role, difficulty, and answer mode — IntervAI
              tailors the questions.
            </p>
            <Button asChild className="mt-2 gap-2">
              <Link href="/dashboard/interviews/new">
                <Plus className="h-4 w-4" />
                Set up your first interview
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {!isLoading && sessions.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2">
          {sessions.map((s) => (
            <div
              key={s.id}
              className="glass-card group relative rounded-xl border border-border/60 p-5 transition-all hover:border-primary/50 hover:shadow-md"
            >
              <div className="absolute right-3 top-3 z-10">
                <DeleteInterviewDialog
                  sessionId={s.id}
                  sessionTitle={s.title}
                  trigger={
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                      onClick={(e) => e.preventDefault()}
                      aria-label="Delete interview"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  }
                />
              </div>
              <Link href={`/dashboard/interviews/${s.id}`} className="block pr-8">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="line-clamp-2 text-sm font-semibold leading-snug">{s.title}</h3>
                  <Badge variant="secondary" className={`shrink-0 ${statusTone(s.status)}`}>
                    {statusLabel(s.status)}
                  </Badge>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{s.target_role}</p>
                <div className="mt-3 flex flex-wrap gap-1.5 text-[11px]">
                  <Badge variant="outline" className="border-border/60">
                    {categoryLabel(s.category)}
                  </Badge>
                  <Badge variant="outline" className="border-border/60">
                    {difficultyLabel(s.difficulty)}
                  </Badge>
                  <Badge variant="outline" className="border-border/60">
                    {s.question_count} Qs
                  </Badge>
                  <Badge variant="outline" className="border-border/60">
                    {answerModeLabel(s.answer_mode)}
                  </Badge>
                </div>
                <p className="mt-3 text-[11px] text-muted-foreground">
                  Created {formatRelativeTime(s.created_at)}
                </p>
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function formatRelativeTime(iso: string): string {
  const date = new Date(iso);
  const diff = Date.now() - date.getTime();
  const minutes = Math.round(diff / 60_000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} hr${hours === 1 ? "" : "s"} ago`;
  const days = Math.round(hours / 24);
  if (days < 30) return `${days} day${days === 1 ? "" : "s"} ago`;
  return date.toLocaleDateString();
}
