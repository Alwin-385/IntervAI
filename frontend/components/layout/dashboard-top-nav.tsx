"use client";

import { Menu, Search } from "lucide-react";

import { UserNav } from "@/components/auth/user-nav";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useBackendUser } from "@/hooks/use-backend-user";

interface DashboardTopNavProps {
  onMenuClick: () => void;
  title?: string;
}

export function DashboardTopNav({ onMenuClick, title = "Overview" }: DashboardTopNavProps) {
  const { data: user, isLoading } = useBackendUser();

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between gap-4 border-b border-border/60 bg-background/80 px-4 backdrop-blur-xl md:px-8">
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
          aria-label="Open sidebar"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <div>
          <p className="text-xs text-muted-foreground">Workspace</p>
          <h1 className="text-lg font-semibold leading-tight">{title}</h1>
        </div>
      </div>

      <div className="hidden max-w-md flex-1 md:flex">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="search"
            placeholder="Search sessions, resumes…"
            className="h-10 w-full rounded-lg border border-border/60 bg-muted/30 pl-10 pr-4 text-sm outline-none ring-primary/50 transition focus:ring-2"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        {isLoading ? (
          <Skeleton className="h-9 w-28" />
        ) : (
          <span className="hidden text-sm text-muted-foreground sm:inline">
            {user?.email}
          </span>
        )}
        <UserNav />
      </div>
    </header>
  );
}
