import { WeakAreasPreview } from "@/features/dashboard/components/weak-areas-preview";

export default function WeakAreasPage() {
  return (
    <div className="p-4 md:p-8">
      <h1 className="mb-6 text-2xl font-bold">Weak areas</h1>
      <WeakAreasPreview />
    </div>
  );
}
