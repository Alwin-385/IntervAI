import { Route } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function RoadmapsPage() {
  return (
    <div className="p-4 md:p-8">
      <h1 className="text-2xl font-bold">Roadmaps</h1>
      <p className="mt-2 text-muted-foreground">Personalized learning paths — next phase.</p>
      <Card className="glass-card mt-8 max-w-xl border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Route className="h-5 w-5 text-accent" />
            Learning roadmaps
          </CardTitle>
          <CardDescription>Milestones and progress tracking coming soon.</CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Build your prep plan from identified weak areas.
        </CardContent>
      </Card>
    </div>
  );
}
