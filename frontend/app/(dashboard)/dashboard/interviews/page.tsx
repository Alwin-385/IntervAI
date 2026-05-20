import { Mic } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function InterviewsPage() {
  return (
    <div className="p-4 md:p-8">
      <Badge variant="secondary" className="mb-4">
        Coming soon
      </Badge>
      <h1 className="text-2xl font-bold">Interview sessions</h1>
      <p className="mt-2 text-muted-foreground">
        AI-powered mock interviews arrive in the next phase.
      </p>
      <Card className="glass-card mt-8 max-w-xl border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mic className="h-5 w-5 text-primary" />
            Mock interviews
          </CardTitle>
          <CardDescription>Start sessions from the dashboard quick actions.</CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          API ready: <code className="rounded bg-muted px-1.5 py-0.5 text-xs">POST /api/v1/interview-sessions</code>
        </CardContent>
      </Card>
    </div>
  );
}
