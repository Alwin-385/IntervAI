import { CtaSection } from "@/features/landing/components/cta-section";
import { DemoSection } from "@/features/landing/components/demo-section";
import { FeaturesSection } from "@/features/landing/components/features-section";
import { HeroSection } from "@/features/landing/components/hero-section";
import { WorkflowSection } from "@/features/landing/components/workflow-section";

export function LandingPage() {
  return (
    <>
      <HeroSection />
      <FeaturesSection />
      <WorkflowSection />
      <DemoSection />
      <CtaSection />
    </>
  );
}
