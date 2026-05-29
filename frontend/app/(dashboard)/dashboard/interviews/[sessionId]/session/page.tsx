import { InterviewSessionPage } from "@/features/interviews/components/interview-session-page";

interface PageProps {
  params: Promise<{ sessionId: string }>;
}

export default async function InterviewSessionRunRoute({ params }: PageProps) {
  const { sessionId } = await params;
  return <InterviewSessionPage sessionId={sessionId} />;
}
