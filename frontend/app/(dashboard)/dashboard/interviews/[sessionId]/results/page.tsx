import { InterviewResultsPage } from "@/features/interviews/components/interview-results-page";

interface PageProps {
  params: Promise<{ sessionId: string }>;
}

export default async function InterviewResultsRoute({ params }: PageProps) {
  const { sessionId } = await params;
  return <InterviewResultsPage sessionId={sessionId} />;
}
