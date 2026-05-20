"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Mic, TrendingUp } from "lucide-react";

import { SectionReveal } from "@/components/motion/section-reveal";
import { AnimatedCounter } from "@/components/motion/animated-counter";
import { Badge } from "@/components/ui/badge";

const scores = [
  { label: "Relevance", value: 88 },
  { label: "Depth", value: 76 },
  { label: "Clarity", value: 92 },
];

export function DemoSection() {
  return (
    <SectionReveal
      id="demo"
      className="section-padding border-y border-border/40 bg-gradient-to-b from-muted/20 to-background"
    >
      <div className="mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-2 lg:gap-16">
        <div>
          <Badge className="mb-4 border-primary/30 bg-primary/10 text-primary">
            AI interview demo
          </Badge>
          <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
            See how candidates get{" "}
            <span className="text-gradient">actionable feedback</span>
          </h2>
          <p className="mt-4 text-muted-foreground">
            Every answer is evaluated across multiple dimensions. Speech metrics
            and structured scores help you improve faster than practicing alone.
          </p>
          <ul className="mt-8 space-y-3">
            {[
              "Real-time follow-up questions",
              "STAR method coaching hints",
              "Exportable session summaries",
            ].map((item) => (
              <li key={item} className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        <motion.div
          initial={{ opacity: 0, x: 24 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          className="glass-card glow-accent rounded-2xl p-6 md:p-8"
        >
          <div className="flex items-center justify-between border-b border-border/50 pb-4">
            <div className="flex items-center gap-2">
              <Mic className="h-5 w-5 text-accent" />
              <span className="font-medium">Session evaluation</span>
            </div>
            <Badge variant="success">Completed</Badge>
          </div>

          <div className="mt-6 flex items-baseline gap-2">
            <span className="text-sm text-muted-foreground">Overall score</span>
            <span className="text-4xl font-bold text-gradient">
              <AnimatedCounter value={85} suffix="%" />
            </span>
          </div>

          <div className="mt-8 space-y-4">
            {scores.map((score, i) => (
              <div key={score.label}>
                <div className="mb-1.5 flex justify-between text-sm">
                  <span className="text-muted-foreground">{score.label}</span>
                  <span className="font-medium">
                    <AnimatedCounter value={score.value} delay={i * 0.1} />
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${score.value}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, delay: 0.2 + i * 0.1 }}
                    className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex items-center gap-2 rounded-lg border border-border/50 bg-muted/30 px-4 py-3 text-sm text-muted-foreground">
            <TrendingUp className="h-4 w-4 text-primary" />
            +12% clarity vs. last session
          </div>
        </motion.div>
      </div>
    </SectionReveal>
  );
}
