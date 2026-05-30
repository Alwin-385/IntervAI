"use client";

import { BarChart3, Brain, FileSearch, Mic, Shield, Sparkles } from "lucide-react";

import { SectionReveal } from "@/components/motion/section-reveal";
import { SectionHeader } from "@/components/shared/section-header";

const features = [
  {
    icon: Brain,
    title: "Adaptive mock interviews",
    description:
      "LangGraph agents generate role-specific questions that follow up on your answers like a real interviewer.",
    gradient: "from-primary/20 to-transparent",
  },
  {
    icon: Mic,
    title: "Speech & delivery analysis",
    description:
      "Measure pace, filler words, and confidence so you sound polished on camera and in person.",
    gradient: "from-accent/20 to-transparent",
  },
  {
    icon: FileSearch,
    title: "Resume intelligence",
    description:
      "Upload your CV, extract skills and gaps, and align practice sessions to what hiring managers care about.",
    gradient: "from-emerald-500/15 to-transparent",
  },
  {
    icon: BarChart3,
    title: "Structured scoring",
    description:
      "Technical, behavioral, and communication dimensions — scored consistently every session.",
    gradient: "from-amber-500/15 to-transparent",
  },
  {
    icon: Shield,
    title: "Enterprise-grade auth",
    description:
      "Clerk-powered sign-in, JWT-secured API, and synced profiles — production security from day one.",
    gradient: "from-primary/15 to-transparent",
  },
  {
    icon: Sparkles,
    title: "Personalized roadmaps",
    description:
      "Weak areas become actionable learning paths so improvement is measurable week over week.",
    gradient: "from-accent/15 to-transparent",
  },
];

export function FeaturesSection() {
  return (
    <SectionReveal id="features" className="section-padding border-t border-border/40 bg-muted/10">
      <div className="mx-auto max-w-6xl">
        <SectionHeader
          badge="Platform"
          title="Everything you need to interview with confidence"
          description="Built for candidates who want recruiter-grade preparation without generic question banks."
        />

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="glass-card group rounded-2xl p-6 transition-all duration-300 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div
                className={`mb-5 inline-flex rounded-xl bg-gradient-to-br ${feature.gradient} p-3`}
              >
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </SectionReveal>
  );
}
