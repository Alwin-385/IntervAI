import { WeakAreasPageContent } from "@/features/weak-areas/components/weak-areas-page-content";

export default function WeakAreasPage() {
  return (
    <div className="mx-auto max-w-5xl space-y-6 p-4 md:p-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Weak areas</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Recurring patterns from your answer quality and speech analysis history.
        </p>
      </div>
      <WeakAreasPageContent />
    </div>
  );
}
