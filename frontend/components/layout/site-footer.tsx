import { env } from "@/lib/env";

export function SiteFooter() {
  return (
    <footer className="border-t border-border/60 py-8">
      <div className="mx-auto max-w-6xl px-6 text-center text-sm text-muted-foreground">
        © {new Date().getFullYear()} {env.appName}. All rights reserved.
      </div>
    </footer>
  );
}
