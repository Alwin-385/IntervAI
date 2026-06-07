"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, FileUp, Mic, Target } from "lucide-react";

import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const actions = [
  {
    title: "Start mock interview",
    description: "Launch an AI-powered practice session",
    href: "/dashboard/interviews",
    icon: Mic,
    primary: true,
  },
  {
    title: "Upload resume",
    description: "Get skill gaps and tailored questions",
    href: "/dashboard/resumes",
    icon: FileUp,
    primary: false,
  },
  {
    title: "Review weak areas",
    description: "Focus on skills that need improvement",
    href: "/dashboard/weak-areas",
    icon: Target,
    primary: false,
  },
];

export function QuickActions() {
  return (
    <Card className="glass-card h-full border-border/50">
      <CardHeader>
        <CardTitle>Quick actions</CardTitle>
        <CardDescription>Jump into your prep workflow</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {actions.map((action, index) => (
          <motion.div
            key={action.title}
            className="w-full"
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.15 + index * 0.06 }}
          >
            <Link
              href={action.href}
              className={cn(
                buttonVariants({ variant: action.primary ? "default" : "outline" }),
                "grid h-auto w-full grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-x-3 px-4 py-3.5",
              )}
            >
              <action.icon className="h-5 w-5 shrink-0" aria-hidden />
              <span className="min-w-0 text-left leading-snug">
                <span className="block font-medium">{action.title}</span>
                <span className="mt-0.5 block text-xs font-normal opacity-80">
                  {action.description}
                </span>
              </span>
              <ArrowRight className="h-4 w-4 shrink-0 opacity-60" aria-hidden />
            </Link>
          </motion.div>
        ))}
      </CardContent>
    </Card>
  );
}
