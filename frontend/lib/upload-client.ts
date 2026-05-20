import { getApiBaseUrl } from "@/lib/env";

export class UploadError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: unknown,
  ) {
    super(message);
    this.name = "UploadError";
  }
}

export interface UploadResumeOptions {
  file: File;
  token: string;
  title?: string;
  replaceResumeId?: string;
  onProgress?: (percent: number) => void;
}

export interface UploadResumeResult {
  ok: true;
  data: unknown;
}

export function uploadResume({
  file,
  token,
  title,
  replaceResumeId,
  onProgress,
}: UploadResumeOptions): Promise<UploadResumeResult> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);
    if (replaceResumeId) formData.append("replace_resume_id", replaceResumeId);

    const xhr = new XMLHttpRequest();
    const url = `${getApiBaseUrl()}/api/v1/resumes/upload`;

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
        resolve({ ok: true, data: body });
        return;
      }

      const message =
        typeof body === "object" &&
        body !== null &&
        "error" in body &&
        typeof (body as { error?: { message?: string } }).error?.message === "string"
          ? (body as { error: { message: string } }).error.message
          : `Upload failed (${xhr.status})`;

      reject(new UploadError(message, xhr.status, body));
    });

    xhr.addEventListener("error", () => {
      reject(new UploadError("Network error during upload", 0));
    });

    xhr.addEventListener("abort", () => {
      reject(new UploadError("Upload cancelled", 0));
    });

    xhr.open("POST", url);
    xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    xhr.send(formData);
  });
}
