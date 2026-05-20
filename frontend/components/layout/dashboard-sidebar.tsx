"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  FileText,
  LayoutDashboard,
  Mic,
  Route,
  Sparkles,
  Target,
  X,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/interviews", label: "Interviews", icon: Mic },
  { href: "/dashboard/resumes", label: "Resumes", icon: FileText },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/weak-areas", label: "Weak Areas", icon: Target },
  { href: "/dashboard/roadmaps", label: "Roadmaps", icon: Route },
];

interface DashboardSidebarProps {
  mobileOpen?: boolean;
  onClose?: () => void;
  className?: string;
}

export function DashboardSidebar({
  mobileOpen = false,
  onClose,
  className,
}: DashboardSidebarProps) {
  const pathname = usePathname();

  const content = (
    <>
      <div className="flex h-16 items-center justify-between border-b border-border/60 px-6">
        <Link href="/dashboard" className="flex items-center gap-2 font-semibold">
          <Sparkles className="h-5 w-5 text-primary" />
          IntervAI
        </Link>
        {onClose && (
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        )}
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => {
          const active =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                active
                  ? "bg-primary/15 text-primary shadow-sm shadow-primary/10"
                  : "text-muted-foreground hover:bg-muted/80 hover:text-foreground",
              )}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-border/60 p-4">
        <div className="rounded-lg border border-border/50 bg-gradient-to-br from-primary/10 to-accent/5 p-4">
          <p className="text-xs font-medium text-primary">Pro tip</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Run one mock interview per week to see measurable score gains.
          </p>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className={cn(
          "hidden h-full w-64 shrink-0 flex-col border-r border-border/60 bg-card/40 lg:flex",
          className,
        )}
      >
        {content}
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            onClick={onClose}
            aria-hidden
          />
          <aside className="absolute left-0 top-0 flex h-full w-72 flex-col border-r border-border/60 bg-card shadow-xl">
            {content}
          </aside>
        </div>
      )}
    </>
  );
}
