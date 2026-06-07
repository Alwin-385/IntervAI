import { getApiBaseUrl } from "@/lib/env";
import { fetchWithAuth, type ClerkGetToken, type TokenRefresh } from "@/lib/auth-client";
import type {
  SpeechAnalysisResult,
  SpeechAnalyzeRequest,
  SpeechCapabilities,
  SpeechSessionResults,
  TranscribeOptions,
  TranscribeResponse,
} from "@/features/speech/types";

export type Auth = { getToken?: ClerkGetToken; refreshToken?: TokenRefresh; token?: string };

function refreshFromAuth(auth: Auth): TokenRefresh | undefined {
  return auth.refreshToken ?? (auth.getToken ? () => auth.getToken!({ skipCache: true }) : undefined);
}

async function parseJsonResponse<T>(
  auth: Auth,
  url: string,
  init: RequestInit | undefined,
): Promise<T> {
  const token = auth.token ?? (auth.getToken ? await auth.getToken() : null);
  if (!token) throw new Error("Not authenticated");
  const res = await fetchWithAuth(token, url, init, refreshFromAuth(auth));
  const body = await res.json();
  if (!res.ok) {
    throw new Error(parseError(body));
  }
  return body as T;
}

export async function fetchSpeechCapabilities(auth: Auth): Promise<SpeechCapabilities> {
  return parseJsonResponse<SpeechCapabilities>(
    auth,
    `${getApiBaseUrl()}/api/v1/speech/capabilities`,
    undefined,
  );
}

export function transcribeAudio({
  file,
  filename,
  token,
  refreshToken,
  getToken,
  sessionId,
  questionId,
  durationSeconds,
  browserTranscript,
  previousTranscript,
  onProgress,
}: TranscribeOptions): Promise<TranscribeResponse> {
  const auth: Auth = { token, refreshToken, getToken };
  const refresh = refreshFromAuth(auth);

  const send = (authToken: string, retried: boolean): Promise<TranscribeResponse> =>
    new Promise((resolve, reject) => {
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
        void (async () => {
          if (xhr.status === 401 && refresh && !retried) {
            const freshToken = await refresh();
            if (freshToken) {
              try {
                resolve(await send(freshToken, true));
              } catch (err) {
                reject(err);
              }
              return;
            }
          }

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
          reject(new Error(parseError(body)));
        })();
      });

      xhr.addEventListener("error", () => {
        reject(new Error("Failed to upload audio for transcription."));
      });

      xhr.open("POST", url);
      xhr.setRequestHeader("Authorization", `Bearer ${authToken}`);
      xhr.send(formData);
    });

  return send(token, false);
}

export async function analyzeSpeech(
  auth: Auth,
  payload: SpeechAnalyzeRequest,
): Promise<SpeechAnalysisResult> {
  return parseJsonResponse<SpeechAnalysisResult>(auth, `${getApiBaseUrl()}/api/v1/speech/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function fetchSpeechSessionResults(
  auth: Auth,
  sessionId: string,
): Promise<SpeechSessionResults> {
  return parseJsonResponse<SpeechSessionResults>(
    auth,
    `${getApiBaseUrl()}/api/v1/speech/session/${sessionId}/results`,
    undefined,
  );
}

export async function fetchSpeechAnalysis(
  auth: Auth,
  answerId: string,
): Promise<SpeechAnalysisResult> {
  return parseJsonResponse<SpeechAnalysisResult>(
    auth,
    `${getApiBaseUrl()}/api/v1/speech/analysis/${answerId}`,
    undefined,
  );
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
