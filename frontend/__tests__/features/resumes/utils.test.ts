/**
 * Unit tests for resume utility functions.
 */

import {
  normalizeResumeStatus,
  normalizeResume,
  normalizeResumeList,
  contactEntries,
  hasExtractedContent,
  extractionStepIndex,
  CONTACT_LABELS,
} from "@/features/resumes/utils";
import type { ExtractedResumeData } from "@/features/resumes/types";

describe("normalizeResumeStatus", () => {
  it("maps legacy 'uploaded' -> 'queued'", () => {
    expect(normalizeResumeStatus("uploaded")).toBe("queued");
  });

  it("maps legacy 'processing' -> 'extracting_resume'", () => {
    expect(normalizeResumeStatus("processing")).toBe("extracting_resume");
  });

  it("maps legacy 'ready' -> 'completed'", () => {
    expect(normalizeResumeStatus("ready")).toBe("completed");
  });

  it("passes through known statuses unchanged", () => {
    expect(normalizeResumeStatus("queued")).toBe("queued");
    expect(normalizeResumeStatus("completed")).toBe("completed");
    expect(normalizeResumeStatus("failed")).toBe("failed");
  });

  it("falls back to 'queued' for unknown status", () => {
    expect(normalizeResumeStatus("unknown_status")).toBe("queued");
  });
});

describe("normalizeResume", () => {
  it("normalizes status field", () => {
    const raw = { id: "1", status: "ready", extracted_data: null };
    const result = normalizeResume(raw);
    expect(result.status).toBe("completed");
  });

  it("preserves all other fields", () => {
    const raw = { id: "abc", status: "completed", extracted_data: null, title: "My Resume" };
    const result = normalizeResume(raw);
    expect(result.id).toBe("abc");
    expect(result.title).toBe("My Resume");
  });

  it("sets extracted_data to null when undefined", () => {
    const raw = { id: "1", status: "completed" };
    const result = normalizeResume(raw);
    expect(result.extracted_data).toBeNull();
  });
});

describe("normalizeResumeList", () => {
  it("normalizes all items in list", () => {
    const data = {
      items: [
        { id: "1", status: "uploaded" },
        { id: "2", status: "ready" },
      ],
      total: 2,
      page: 1,
      page_size: 20,
      pages: 1,
    };
    const result = normalizeResumeList(data as any);
    expect(result.items[0].status).toBe("queued");
    expect(result.items[1].status).toBe("completed");
  });
});

describe("extractionStepIndex", () => {
  it("returns 0 for queued", () => {
    expect(extractionStepIndex("queued")).toBe(0);
  });

  it("returns 1 for extracting_resume", () => {
    expect(extractionStepIndex("extracting_resume")).toBe(1);
  });

  it("returns 3 for completed", () => {
    expect(extractionStepIndex("completed")).toBe(3);
  });

  it("returns -1 for failed", () => {
    expect(extractionStepIndex("failed")).toBe(-1);
  });
});

describe("contactEntries", () => {
  it("returns empty array for undefined contact", () => {
    expect(contactEntries(undefined)).toEqual([]);
  });

  it("returns email entry", () => {
    const contact = { email: "john@example.com" };
    const entries = contactEntries(contact);
    expect(entries.some(([, v]) => v === "john@example.com")).toBe(true);
  });

  it("uses CONTACT_LABELS for known keys", () => {
    const contact = { github: "github.com/johndoe" };
    const entries = contactEntries(contact);
    expect(entries.some(([k]) => k === CONTACT_LABELS.github)).toBe(true);
  });

  it("skips empty values", () => {
    const contact = { email: "", phone: "1234567890" };
    const entries = contactEntries(contact);
    expect(entries.some(([, v]) => v === "")).toBe(false);
  });
});

describe("hasExtractedContent", () => {
  const emptyData: ExtractedResumeData = {
    name: null,
    contact: {},
    education: [],
    projects: [],
    experience: [],
    skills: [],
    certifications: [],
    internships: [],
    achievements: [],
  };

  it("returns false for completely empty data", () => {
    expect(hasExtractedContent(emptyData)).toBe(false);
  });

  it("returns true when skills present", () => {
    const data = { ...emptyData, skills: ["Python", "TypeScript"] };
    expect(hasExtractedContent(data)).toBe(true);
  });

  it("returns true when experience present", () => {
    const data = { ...emptyData, experience: ["Google 2023"] };
    expect(hasExtractedContent(data)).toBe(true);
  });
});
