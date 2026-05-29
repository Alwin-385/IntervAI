import { getApiBaseUrl } from "@/lib/env";
import type {
  SpeechAnalysisResult,
  SpeechAnalyzeRequest,
  SpeechCapabilities,
  SpeechSessionResults,
  TranscribeOptions,
  TranscribeResponse,
} from "@/features/speech/types";

export class SpeechApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: unknown,
  ) {
    super(message);
    this.name = "SpeechApiError";
  }
}

export async function fetchSpeechCapabilities(token: string): Promise<SpeechCapabilities> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/speech/capabilities`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  const body = await res.json();
  if (!res.ok) {
    throw new SpeechApiError(parseError(body), res.status, body);
  }
  return body as SpeechCapabilities;
}

export function transcribeAudio({
  file,
  filename,
  token,
  sessionId,
  questionId,
  durationSeconds,
  browserTranscript,
  previousTranscript,
  onProgress,
}: TranscribeOptions): Promise<TranscribeResponse> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append("file", file, filename);
    if (sessionId) formData.append("session_id", sessionId);
    if (questionId) formData.append("question_id", questionId);
    if (durationSeconds != null) {
      formData.append("duration_seconds", String(durationSeconds));
    }
    if (browserTranscript?.trim()) {
      formData.append("browser_transcript", browserTranscript.trim());
    }
    if (previousTranscript?.trim()) {
      formData.append("previous_transcript", previousTranscript.trim());
    }

    const xhr = new XMLHttpRequest();
    const url = `${getApiBaseUrl()}/api/v1/speech/transcribe`;

    xhr.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    });

    xhr.addEventListener("load", () => {
      let body: unknown = null;
      try {
        body = xhr.responseText ? JSON.parse(xhr.responseText) : null;
      } catch {
        body = xhr.responseText;
      }
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(body as TranscribeResponse);
        return;
      }
      reject(new SpeechApiError(parseError(body), xhr.status, body));
    });

    xhr.addEventListener("error", () => {
      reject(new SpeechApiError("Failed to upload audio for transcription.", 0));
    });

    xhr.open("POST", url);
    xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    xhr.send(formData);
  });
}

export async function analyzeSpeech(
  token: string,
  payload: SpeechAnalyzeRequest,
): Promise<SpeechAnalysisResult> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/speech/analyze`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const body = await res.json();
  if (!res.ok) {
    throw new SpeechApiError(parseError(body), res.status, body);
  }
  return body as SpeechAnalysisResult;
}

export async function fetchSpeechSessionResults(
  token: string,
  sessionId: string,
): Promise<SpeechSessionResults> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/speech/session/${sessionId}/results`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  const body = await res.json();
  if (!res.ok) {
    throw new SpeechApiError(parseError(body), res.status, body);
  }
  return body as SpeechSessionResults;
}

export async function fetchSpeechAnalysis(
  token: string,
  answerId: string,
): Promise<SpeechAnalysisResult> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/speech/analysis/${answerId}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  const body = await res.json();
  if (!res.ok) {
    throw new SpeechApiError(parseError(body), res.status, body);
  }
  return body as SpeechAnalysisResult;
}

function parseError(body: unknown): string {
  if (
    typeof body === "object" &&
    body !== null &&
    "error" in body &&
    typeof (body as { error?: { message?: string } }).error?.message === "string"
  ) {
    return (body as { error: { message: string } }).error.message;
  }
  return "Transcription request failed";
}
