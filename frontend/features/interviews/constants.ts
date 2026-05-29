import type { LucideIcon } from "lucide-react";
import {
  BrainCircuit,
  Code2,
  Database,
  FileText,
  Layers,
  Layout,
  LineChart,
  Server,
  Settings2,
  Sparkles,
  Terminal,
  Users,
  Wrench,
  Briefcase,
  GraduationCap,
  Mic,
  Pencil,
  Trophy,
  Lightbulb,
  Flame,
  Rocket,
} from "lucide-react";

import type {
  AnswerMode,
  InterviewCategory,
  InterviewDifficulty,
} from "@/features/interviews/types";

export interface RoleOption {
  value: string;
  label: string;
  icon: LucideIcon;
  blurb: string;
  custom?: boolean;
}

export const PRESET_ROLES: RoleOption[] = [
  {
    value: "Software Engineer",
    label: "Software Engineer",
    icon: Code2,
    blurb: "General software roles, fullstack fundamentals",
  },
  {
    value: "AI Engineer",
    label: "AI Engineer",
    icon: BrainCircuit,
    blurb: "LLMs, prompt design, model integration",
  },
  {
    value: "Frontend Developer",
    label: "Frontend Developer",
    icon: Layout,
    blurb: "React, UI/UX, web performance",
  },
  {
    value: "Backend Developer",
    label: "Backend Developer",
    icon: Server,
    blurb: "APIs, databases, scalability",
  },
  {
    value: "Full Stack Developer",
    label: "Full Stack Developer",
    icon: Layers,
    blurb: "End-to-end ownership, frontend + backend",
  },
  {
    value: "Data Analyst",
    label: "Data Analyst",
    icon: LineChart,
    blurb: "SQL, dashboards, business insights",
  },
  {
    value: "ML Engineer",
    label: "ML Engineer",
    icon: Database,
    blurb: "Model training, MLOps, production ML",
  },
  {
    value: "DevOps Engineer",
    label: "DevOps Engineer",
    icon: Wrench,
    blurb: "CI/CD, infrastructure, reliability",
  },
  {
    value: "",
    label: "Custom role",
    icon: Pencil,
    blurb: "Type your own target role",
    custom: true,
  },
];

export interface CategoryOption {
  value: InterviewCategory;
  label: string;
  icon: LucideIcon;
  blurb: string;
}

export const CATEGORIES: CategoryOption[] = [
  {
    value: "hr",
    label: "HR",
    icon: Users,
    blurb: "Background, motivation, culture fit",
  },
  {
    value: "technical",
    label: "Technical",
    icon: Terminal,
    blurb: "Role-specific concepts and trade-offs",
  },
  {
    value: "behavioral",
    label: "Behavioral",
    icon: Briefcase,
    blurb: "STAR-style situational questions",
  },
  {
    value: "dsa",
    label: "DSA",
    icon: Sparkles,
    blurb: "Data structures and algorithms",
  },
  {
    value: "resume_based",
    label: "Resume-Based",
    icon: FileText,
    blurb: "Questions tailored to your uploaded resume",
  },
  {
    value: "mixed",
    label: "Mixed",
    icon: Settings2,
    blurb: "Balanced set across all categories",
  },
];

export interface DifficultyOption {
  value: InterviewDifficulty;
  label: string;
  icon: LucideIcon;
  blurb: string;
  accent: string;
}

export const DIFFICULTIES: DifficultyOption[] = [
  {
    value: "beginner",
    label: "Beginner",
    icon: GraduationCap,
    blurb: "Fundamentals, internships, first roles",
    accent: "from-emerald-500/20 to-emerald-500/0",
  },
  {
    value: "intermediate",
    label: "Intermediate",
    icon: Lightbulb,
    blurb: "Mid-level: 2–4 years, applied scenarios",
    accent: "from-amber-500/20 to-amber-500/0",
  },
  {
    value: "advanced",
    label: "Advanced",
    icon: Flame,
    blurb: "Senior: depth, trade-offs, system design",
    accent: "from-rose-500/25 to-rose-500/0",
  },
];

export interface AnswerModeOption {
  value: AnswerMode;
  label: string;
  icon: LucideIcon;
  blurb: string;
}

export const ANSWER_MODES: AnswerModeOption[] = [
  {
    value: "text",
    label: "Text",
    icon: Pencil,
    blurb: "Type your answers — easy to revise and review",
  },
  {
    value: "voice",
    label: "Voice",
    icon: Mic,
    blurb: "Speak naturally — practice real interview pace",
  },
];

export const QUESTION_COUNT_PRESETS = [5, 8, 10, 15, 20] as const;
export const MIN_QUESTIONS = 3;
export const MAX_QUESTIONS = 25;

export const STEP_LABELS = [
  "Role",
  "Category",
  "Difficulty",
  "Questions",
  "Answer mode",
  "Review",
] as const;

export const SUMMARY_ICON = Trophy;
export const READY_ICON = Rocket;
