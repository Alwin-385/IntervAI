import type { ExtractedResumeData, PaginatedResumes, Resume, ResumeStatus } from "./types";

const LEGACY_STATUS: Record<string, ResumeStatus> = {
  uploaded: "queued",
  processing: "extracting_resume",
  ready: "completed",
};

export const CONTACT_LABELS: Record<string, string> = {
  email: "Mail",
  phone: "Phone",
  linkedin: "LinkedIn",
  github: "GitHub",
  address: "Address",
  website: "Website",
};

const CONTACT_ORDER = ["email", "phone", "linkedin", "github", "address", "website"] as const;

const INVALID_ADDRESS =
  /dashboard|platform|project|developer|intern|college|university|engineering|github|linkedin|http|@/i;

function isPlausibleAddress(value: string): boolean {
  const text = value.trim();
  if (text.length < 4 || text.length > 160) return false;
  if (INVALID_ADDRESS.test(text)) return false;
  return /,|\b\d{6}\b|\b(india|kerala|state|district)\b/i.test(text);
}

export function normalizeResumeStatus(status: string): ResumeStatus {
  if (status in LEGACY_STATUS) return LEGACY_STATUS[status];
  if (
    status === "queued" ||
    status === "extracting_resume" ||
    status === "completed" ||
    status === "failed"
  ) {
    return status;
  }
  return "queued";
}

export function normalizeExtractedData(
  data: ExtractedResumeData | null | undefined,
): ExtractedResumeData | null {
  if (!data) return null;
  return {
    ...data,
    contact: data.contact ?? {},
  };
}

export function normalizeResume<
  T extends { status: string; extracted_data?: ExtractedResumeData | null },
>(resume: T): T & { status: ResumeStatus; extracted_data: ExtractedResumeData | null } {
  return {
    ...resume,
    status: normalizeResumeStatus(resume.status),
    extracted_data: normalizeExtractedData(resume.extracted_data),
  };
}

export function normalizeResumeList(data: PaginatedResumes): PaginatedResumes {
  return {
    ...data,
    items: data.items.map((r) => normalizeResume(r)),
  };
}

export function contactEntries(contact: Record<string, string> | undefined): [string, string][] {
  if (!contact) return [];
  const entries: [string, string][] = [];
  for (const key of CONTACT_ORDER) {
    const value = contact[key];
    if (!value?.trim()) continue;
    if (key === "address" && !isPlausibleAddress(value)) continue;
    entries.push([CONTACT_LABELS[key] ?? key, value.trim()]);
  }
  for (const [key, value] of Object.entries(contact)) {
    if (!CONTACT_ORDER.includes(key as (typeof CONTACT_ORDER)[number]) && value?.trim()) {
      entries.push([key.charAt(0).toUpperCase() + key.slice(1), value.trim()]);
    }
  }
  return entries;
}

export function hasExtractedContent(data: ExtractedResumeData): boolean {
  return (
    contactEntries(data.contact).length > 0 ||
    data.education.length > 0 ||
    data.experience.length > 0 ||
    data.projects.length > 0 ||
    data.skills.length > 0 ||
    data.certifications.length > 0 ||
    data.internships.length > 0 ||
    data.achievements.length > 0
  );
}

export const EXTRACTION_STEPS: { key: ResumeStatus | "done"; label: string }[] = [
  { key: "queued", label: "Queued" },
  { key: "extracting_resume", label: "Extracting text" },
  { key: "done", label: "Structured & stored" },
];

export function extractionStepIndex(status: ResumeStatus): number {
  if (status === "queued") return 0;
  if (status === "extracting_resume") return 1;
  if (status === "completed") return 3;
  return -1;
}
