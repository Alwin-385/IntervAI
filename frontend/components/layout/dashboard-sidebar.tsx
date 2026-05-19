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
} from "lucide-react";

import { cn } from "@/lib/utils";
import { UserNav } from "@/components/auth/user-nav";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/interviews", label: "Interviews", icon: Mic },
  { href: "/dashboard/resumes", label: "Resumes", icon: FileText },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/weak-areas", label: "Weak Areas", icon: Target },
  { href: "/dashboard/roadmaps", label: "Roadmaps", icon: Route },
];

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-64 flex-col border-r border-border/60 bg-card/40">
      <div className="flex h-16 items-center gap-2 border-b border-border/60 px-6 font-semibold">
        <Sparkles className="h-5 w-5 text-primary" />
        IntervAI
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
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-primary/15 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-border/60 p-4">
        <UserNav />
      </div>
    </aside>
  );
}
