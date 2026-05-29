import { InterviewDetailPage } from "@/features/interviews/components/interview-detail-page";

interface PageProps {
  params: Promise<{ sessionId: string }>;
}

export default async function InterviewSessionRoute({ params }: PageProps) {
  const { sessionId } = await params;
  return <InterviewDetailPage sessionId={sessionId} />;
}
