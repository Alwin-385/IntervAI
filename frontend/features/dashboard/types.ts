export interface DashboardStats {
  mock_interviews: number;
  resumes_total: number;
  resumes_analyzed: number;
  resumes_processing: number;
  average_score: number | null;
  practice_hours: number;
}

export interface DashboardActivityItem {
  kind: string;
  title: string;
  subtitle: string;
  timestamp: string;
  status: string | null;
}

export interface DashboardOverview {
  stats: DashboardStats;
  recent_activity: DashboardActivityItem[];
}
