"use client";

import { motion } from "framer-motion";
import { Play, Sparkles, Zap } from "lucide-react";

import { HeroCta } from "@/features/landing/components/hero-cta";
import { env } from "@/lib/env";

export function HeroSection() {
  return (
    <section className="relative min-h-[90vh] overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-grid-pattern opacity-25"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-gradient-to-b from-primary/25 via-accent/10 to-transparent blur-3xl"
      />

      <div className="relative mx-auto flex max-w-6xl flex-col items-center px-6 pb-16 pt-24 md:pt-32">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-sm text-primary backdrop-blur"
        >
          <Sparkles className="h-4 w-4" />
          {env.appName}
          <span className="rounded-full bg-accent/20 px-2 py-0.5 text-xs text-accent">
            AI-native
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="max-w-4xl text-center text-4xl font-bold leading-[1.1] tracking-tight md:text-6xl lg:text-7xl"
        >
          Hire-ready interviews,{" "}
          <span className="text-gradient">powered by intelligence</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 max-w-2xl text-center text-lg text-muted-foreground md:text-xl"
        >
          Practice role-specific mock interviews, get scored feedback, and track
          weak areas — the modern stack recruiters expect from top candidates.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <HeroCta />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.45 }}
          className="mt-16 w-full max-w-4xl"
        >
          <div className="glass-card glow-primary overflow-hidden rounded-2xl p-1">
            <div className="rounded-xl bg-gradient-to-br from-card via-card to-muted/30 p-6 md:p-8">
              <div className="flex items-center gap-2 border-b border-border/50 pb-4">
                <span className="h-3 w-3 rounded-full bg-red-500/80" />
                <span className="h-3 w-3 rounded-full bg-amber-500/80" />
                <span className="h-3 w-3 rounded-full bg-emerald-500/80" />
                <span className="ml-2 text-xs text-muted-foreground">
                  Live interview preview
                </span>
              </div>
              <div className="mt-6 space-y-4">
                <div className="flex gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/20">
                    <Zap className="h-4 w-4 text-primary" />
                  </div>
                  <div className="rounded-lg rounded-tl-none border border-border/60 bg-muted/30 px-4 py-3 text-sm">
                    Tell me about a time you led a cross-functional project under
                    tight deadlines.
                  </div>
                </div>
                <div className="flex justify-end gap-3">
                  <div className="max-w-[85%] rounded-lg rounded-tr-none border border-primary/30 bg-primary/10 px-4 py-3 text-sm">
                    I aligned engineering and design on a two-week sprint…
                  </div>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Play className="h-3.5 w-3.5" />
                  AI evaluating clarity, depth, and structure…
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
