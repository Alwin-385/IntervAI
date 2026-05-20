import { MarketingHeader } from "@/components/layout/marketing-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { LandingPage } from "@/features/landing/components/landing-page";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <MarketingHeader />
      <main className="flex-1">
        <LandingPage />
      </main>
      <SiteFooter />
    </div>
  );
}
