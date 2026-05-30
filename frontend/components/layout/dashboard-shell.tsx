"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";

import { DashboardSidebar } from "@/components/layout/dashboard-sidebar";
import { DashboardTopNav } from "@/components/layout/dashboard-top-nav";

const pageTitles: Record<string, string> = {
  "/dashboard": "Overview",
  "/dashboard/interviews": "Interviews",
  "/dashboard/resumes": "Resumes",
  "/dashboard/analytics": "Analytics",
  "/dashboard/weak-areas": "Weak Areas",
  "/dashboard/roadmaps": "Roadmaps",
};

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const pathname = usePathname();
  const title = pageTitles[pathname] ?? "Dashboard";

  return (
    <div className="flex min-h-screen bg-background">
      <DashboardSidebar mobileOpen={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <DashboardTopNav title={title} onMenuClick={() => setMobileNavOpen(true)} />
        <div className="flex-1 bg-gradient-to-b from-muted/10 to-background">{children}</div>
      </div>
    </div>
  );
}
