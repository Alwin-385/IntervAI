"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import type { MeResponse } from "@/features/auth/types";

interface WelcomeCardProps {
  user?: MeResponse;
  isLoading: boolean;
}

export function WelcomeCard({ user, isLoading }: WelcomeCardProps) {
  const firstName = user?.full_name?.split(" ")[0] ?? "there";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card glow-primary relative overflow-hidden rounded-2xl border-primary/20 p-6 md:p-8"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-primary/20 blur-3xl"
      />
      <div className="relative flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="mb-2 inline-flex items-center gap-2 text-sm text-primary">
            <Sparkles className="h-4 w-4" />
            Your workspace
          </div>
          {isLoading ? (
            <>
              <Skeleton className="h-9 w-64" />
              <Skeleton className="mt-2 h-4 w-48" />
            </>
          ) : (
            <>
              <h2 className="text-2xl font-bold tracking-tight md:text-3xl">
                Welcome back, {firstName}
              </h2>
              <p className="mt-2 text-muted-foreground">
                {user?.email ?? "Continue your interview preparation journey."}
              </p>
            </>
          )}
        </div>
        {!isLoading && user && (
          <div className="flex items-center gap-3 rounded-xl border border-border/50 bg-muted/30 px-4 py-3">
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt=""
                className="h-12 w-12 rounded-full ring-2 ring-primary/30"
              />
            ) : (
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 text-lg font-semibold text-primary">
                {firstName.charAt(0).toUpperCase()}
              </div>
            )}
            <div>
              <p className="text-sm font-medium">{user.full_name}</p>
              <p className="text-xs capitalize text-muted-foreground">{user.role}</p>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
