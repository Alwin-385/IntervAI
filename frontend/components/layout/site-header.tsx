import Link from "next/link";
import { Sparkles } from "lucide-react";

import { UserNav } from "@/components/auth/user-nav";
import { env } from "@/lib/env";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link
          href="/"
          className="flex items-center gap-2 font-semibold transition-opacity hover:opacity-90"
        >
          <Sparkles className="h-5 w-5 text-primary" />
          <span className="hidden sm:inline">{env.appName}</span>
          <span className="sm:hidden">IntervAI</span>
        </Link>
        <UserNav />
      </div>
    </header>
  );
}
