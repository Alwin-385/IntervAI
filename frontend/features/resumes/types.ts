export type ResumeStatus = "uploaded" | "processing" | "ready" | "failed";

export interface Resume {
  id: string;
  user_id: string;
  title: string;
  file_name: string;
  storage_path: string;
  storage_key: string;
  mime_type: string;
  file_size_bytes: number;
  content_text: string | null;
  status: ResumeStatus;
  created_at: string;
  updated_at: string;
}

export interface ResumeUploadResponse extends Resume {
  message: string;
}

export interface PaginatedResumes {
  items: Resume[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
