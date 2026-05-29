export type TranscriptionSource = "whisper" | "browser";

export type SpeechTranscriptionMode = "browser" | "whisper";

export interface SpeechCapabilities {
  transcription_mode: SpeechTranscriptionMode;
  whisper_available: boolean;
  max_size_bytes: number;
  allowed_extensions: string[];
}

export interface TranscribeResponse {
  transcript: string;
  audio_storage_path: string;
  duration_seconds: number | null;
  mime_type: string;
  file_size_bytes: number;
  transcription_source: TranscriptionSource;
  speech_analysis_id: string | null;
  answer_id: string | null;
  whisper_available: boolean;
}

export interface TranscribeOptions {
  file: Blob;
  filename: string;
  token: string;
  sessionId?: string;
  questionId?: string;
  durationSeconds?: number;
  browserTranscript?: string;
  previousTranscript?: string;
  onProgress?: (percent: number) => void;
}

export interface FillerWordStat {
  word: string;
  count: number;
}

/** Normalized speech analysis — mirrors resume `StructuredResumeAnalysis` shape. */
export interface SpeechAnalysisScores {
  communication_score: number;
  fluency_score: number;
  confidence_score: number;
  speaking_speed_score: number;
  pause_score: number;
}

export interface SpeechDeliveryBreakdown {
  words_per_minute: number;
  filler_word_count: number;
  pause_count: number;
  hesitation_count: number;
  pace_label: string;
}

export interface StructuredSpeechAnalysis {
  version: string;
  role_target?: string | null;
  question_label?: string | null;
  scores: SpeechAnalysisScores;
  delivery: SpeechDeliveryBreakdown;
  skill_radar: Record<string, number>;
  filler_breakdown: FillerWordStat[];
  confidence_indicators: Record<string, number>;
  weak_patterns: string[];
  communication_tips: string[];
  strengths: string[];
  word_count: number;
}

export interface SpeechAnalysisResult {
  id: string;
  answer_id: string | null;
  session_id: string | null;
  fluency_score: number;
  communication_score: number;
  confidence_score: number;
  speaking_speed_score: number;
  pause_score: number;
  words_per_minute: number;
  filler_word_count: number;
  filler_word_stats: FillerWordStat[];
  pause_count: number;
  hesitation_count: number;
  weak_patterns: string[];
  communication_tips: string[];
  confidence_indicators: Record<string, number>;
  metrics: Record<string, unknown>;
  clarity_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface SpeechAnalyzeRequest {
  answer_id: string;
  transcript?: string;
  duration_seconds?: number;
}

export interface SessionSpeechSummary {
  analyzed_count: number;
  skipped_count: number;
  avg_communication_score: number;
  avg_fluency_score: number;
  avg_confidence_score: number;
  avg_speaking_speed_score: number;
  avg_words_per_minute: number;
  total_filler_words: number;
  highlight_weak_patterns: string[];
  highlight_tips: string[];
}

export interface QuestionSpeechAnalysis {
  question_id: string;
  question_text: string;
  order_index: number;
  answer_id: string | null;
  answer_preview: string;
  analysis: SpeechAnalysisResult | null;
}

export interface SpeechSessionResults {
  session_id: string;
  session_title: string;
  target_role: string;
  questions: QuestionSpeechAnalysis[];
  summary: SessionSpeechSummary;
}

export type SpeechAnalysisRevealStep =
  | "scores"
  | "speed"
  | "fillers"
  | "charts"
  | "confidence"
  | "weak"
  | "tips";
