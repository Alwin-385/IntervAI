export type ResumeStatus =
  | "queued"
  | "extracting_resume"
  | "completed"
  | "failed";

export interface ExtractedResumeData {
  name: string | null;
  contact?: Record<string, string>;
  education: string[];
  projects: string[];
  experience: string[];
  skills: string[];
  certifications: string[];
  internships: string[];
  achievements: string[];
}

export interface ResumeTextChunk {
  index: number;
  text: string;
  char_start: number;
  char_end: number;
}

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
  cleaned_text: string | null;
  extracted_data: ExtractedResumeData | null;
  text_chunks: ResumeTextChunk[] | null;
  extraction_error: string | null;
  status: ResumeStatus;
  created_at: string;
  updated_at: string;
}

export interface ResumeUploadResponse extends Resume {
  message: string;
}

export interface ResumeExtractionStatus {
  id: string;
  resume_id: string;
  status: ResumeStatus;
  extraction_error: string | null;
  has_cleaned_text: boolean;
  chunk_count: number;
  extracted_data: ExtractedResumeData | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResumes {
  items: Resume[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export const EXTRACTION_POLL_STATUSES: readonly ResumeStatus[] = [
  "queued",
  "extracting_resume",
];
