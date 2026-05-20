import { FileText } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ResumesPage() {
  return (
    <div className="p-4 md:p-8">
      <h1 className="text-2xl font-bold">Resumes</h1>
      <p className="mt-2 text-muted-foreground">Upload and analyze resumes — next phase.</p>
      <Card className="glass-card mt-8 max-w-xl border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Resume library
          </CardTitle>
          <CardDescription>Drag-and-drop upload UI coming soon.</CardDescription>
        </CardHeader>
        <CardContent className="flex h-40 items-center justify-center rounded-lg border border-dashed border-border/60 text-sm text-muted-foreground">
          No resumes uploaded yet
        </CardContent>
      </Card>
    </div>
  );
}
