"use client";

import { motion } from "framer-motion";
import { ArrowRight, Brain, Mic, Sparkles, Target } from "lucide-react";

import { Button } from "@/components/ui/button";
import { env } from "@/lib/env";

const features = [
  {
    icon: Brain,
    title: "AI Mock Interviews",
    description: "Role-specific sessions powered by LangGraph agents.",
  },
  {
    icon: Target,
    title: "Skill Evaluation",
    description: "Structured scoring across technical and behavioral dimensions.",
  },
  {
    icon: Mic,
    title: "Speech Analysis",
    description: "Real-time feedback on clarity, pace, and confidence.",
  },
];

export function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-grid-pattern opacity-30"
      />

      <div
        aria-hidden
        className="pointer-events-none absolute -left-32 top-20 h-72 w-72 rounded-full bg-primary/20 blur-3xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-32 top-40 h-96 w-96 rounded-full bg-accent/20 blur-3xl"
      />

      <div className="relative mx-auto max-w-6xl px-6 pb-24 pt-20 md:pt-28">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mx-auto max-w-3xl text-center"
        >
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/60 px-4 py-1.5 text-sm text-muted-foreground backdrop-blur">
            <Sparkles className="h-4 w-4 text-accent" />
            {env.appName}
          </div>

          <h1 className="text-4xl font-bold tracking-tight md:text-6xl md:leading-tight">
            Ace your next interview with{" "}
            <span className="text-gradient">AI intelligence</span>
          </h1>
          <p className="mt-6 text-lg text-muted-foreground md:text-xl">
            Prepare, practice, and get evaluated with production-grade AI —
            from mock interviews to detailed performance analytics.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button size="lg" className="gap-2 px-8">
              Get started
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button size="lg" variant="outline">
              View demo
            </Button>
          </div>
        </motion.div>

        <div className="mt-20 grid gap-6 md:grid-cols-3">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              className="rounded-xl border border-border/60 bg-card/60 p-6 backdrop-blur-sm"
            >
              <feature.icon className="mb-4 h-8 w-8 text-primary" />
              <h3 className="font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
