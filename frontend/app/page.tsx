import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { HealthStatus } from "@/features/health/components/health-status";
import { HeroSection } from "@/features/landing/components/hero-section";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="flex-1">
        <HeroSection />
        <section className="mx-auto max-w-6xl px-6 pb-24">
          <HealthStatus />
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
