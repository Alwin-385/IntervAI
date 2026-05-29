export type RoadmapPhaseKind = "immediate" | "short_term" | "advanced";
export type RoadmapItemPriority = "high" | "medium" | "low";

export interface RoadmapItem {
  id: string;
  title: string;
  description: string;
  priority: RoadmapItemPriority;
  phase: RoadmapPhaseKind;
  category: string;
  estimated_time: string;
  practice_recommendation: string;
  resources: string[];
  weak_area_kind: string | null;
  completed: boolean;
  completed_at: string | null;
}

export interface RoadmapPhase {
  phase: RoadmapPhaseKind;
  title: string;
  subtitle: string;
  estimated_duration: string;
  items: RoadmapItem[];
}

export interface GeneratedRoadmap {
  id: string;
  created_at: string;
  updated_at: string;
  title: string;
  description: string | null;
  target_role: string | null;
  status: string;
  phases: RoadmapPhase[];
  summary: string;
  total_items: number;
  weak_areas_addressed: string[];
  generated_at: string;
  job_id?: string | null;
}
