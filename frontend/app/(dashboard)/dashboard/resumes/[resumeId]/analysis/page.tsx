import { ResumeAnalysisPage } from "@/features/resume-analysis/components/resume-analysis-page";

interface PageProps {
  params: Promise<{ resumeId: string }>;
}

export default async function ResumeAnalysisRoute({ params }: PageProps) {
  const { resumeId } = await params;
  return <ResumeAnalysisPage resumeId={resumeId} />;
}
