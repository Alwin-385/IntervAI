"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

import { HeroCta } from "@/features/landing/components/hero-cta";
import { SectionReveal } from "@/components/motion/section-reveal";

export function CtaSection() {
  return (
    <SectionReveal className="section-padding">
      <div className="mx-auto max-w-6xl px-6">
        <motion.div
          whileInView={{ opacity: 1, scale: 1 }}
          initial={{ opacity: 0.95, scale: 0.98 }}
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-3xl border border-primary/30 bg-gradient-to-br from-primary/20 via-card to-accent/15 p-10 text-center md:p-16"
        >
          <div
            aria-hidden
            className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/30 blur-3xl"
          />
          <div
            aria-hidden
            className="pointer-events-none absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-accent/25 blur-3xl"
          />

          <h2 className="relative text-3xl font-bold md:text-4xl">
            Ready to impress your next interviewer?
          </h2>
          <p className="relative mx-auto mt-4 max-w-xl text-muted-foreground">
            Join candidates using AI-powered prep to land offers at top companies. Start free — no
            credit card required.
          </p>
          <div className="relative mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <HeroCta />
          </div>
          <p className="relative mt-6 flex items-center justify-center gap-1 text-xs text-muted-foreground">
            <ArrowRight className="h-3 w-3" />
            Setup takes less than 2 minutes
          </p>
        </motion.div>
      </div>
    </SectionReveal>
  );
}
