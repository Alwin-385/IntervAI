"use client";

import { motion } from "framer-motion";
import { ArrowRight, LineChart, MessageSquare, Upload } from "lucide-react";

import { SectionReveal } from "@/components/motion/section-reveal";
import { SectionHeader } from "@/components/shared/section-header";

const steps = [
  {
    step: "01",
    icon: Upload,
    title: "Upload your resume",
    description:
      "We parse skills, experience, and gaps to tailor every session to your target role.",
  },
  {
    step: "02",
    icon: MessageSquare,
    title: "Run mock interviews",
    description:
      "Practice technical and behavioral rounds with AI that probes deeper on weak answers.",
  },
  {
    step: "03",
    icon: LineChart,
    title: "Review scores & roadmaps",
    description:
      "See dimension-level feedback, track progress, and follow a personalized improvement plan.",
  },
];

export function WorkflowSection() {
  return (
    <SectionReveal id="workflow" className="section-padding">
      <div className="mx-auto max-w-6xl">
        <SectionHeader
          badge="How it works"
          title="From resume to offer-ready in three steps"
          description="A clear workflow designed for busy professionals preparing for high-stakes interviews."
        />

        <div className="relative mt-16">
          <div
            aria-hidden
            className="absolute left-0 right-0 top-1/2 hidden h-px bg-gradient-to-r from-transparent via-border to-transparent lg:block"
          />

          <div className="grid gap-8 lg:grid-cols-3">
            {steps.map((item, index) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.12 }}
                className="relative glass-card rounded-2xl p-8"
              >
                <span className="text-5xl font-bold text-muted/30">{item.step}</span>
                <div className="mt-4 inline-flex rounded-lg bg-primary/15 p-2.5">
                  <item.icon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="mt-4 text-xl font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{item.description}</p>
                {index < steps.length - 1 && (
                  <ArrowRight className="absolute -right-4 top-1/2 hidden h-6 w-6 text-muted-foreground lg:block" />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}
