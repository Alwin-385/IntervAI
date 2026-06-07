import { DashboardShell } from "@/components/layout/dashboard-shell";

/** Auth is enforced in middleware (clerkMiddleware + auth.protect). */
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <DashboardShell>{children}</DashboardShell>;
}
