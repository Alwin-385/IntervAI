import { Mic } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function InterviewsPage() {
  return (
    <div className="p-8">
      <Badge variant="secondary" className="mb-3">
        Coming soon
      </Badge>
      <h1 className="text-2xl font-bold">Interview sessions</h1>
      <Card className="mt-6 border-border/60 bg-card/80">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mic className="h-5 w-5 text-primary" />
            Mock interviews
          </CardTitle>
          <CardDescription>AI-powered sessions will be available in the next phase.</CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Your authenticated API is ready at{" "}
          <code className="rounded bg-muted px-1">POST /api/v1/interview-sessions</code>.
        </CardContent>
      </Card>
    </div>
  );
}
