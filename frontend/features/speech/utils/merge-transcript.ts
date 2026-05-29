/** Normalize text for overlap comparison. */
export function normalizeTranscript(s: string): string {
  return s.trim().replace(/\s+/g, " ").toLowerCase();
}

function wordCount(s: string): number {
  return s.trim().split(/\s+/).filter(Boolean).length;
}

/** Words shared at the start of both strings. */
export function longestCommonPrefixWords(a: string, b: string): number {
  const aWords = a.trim().split(/\s+/).filter(Boolean);
  const bWords = b.trim().split(/\s+/).filter(Boolean);
  let i = 0;
  while (i < aWords.length && i < bWords.length) {
    if (aWords[i]!.toLowerCase() !== bWords[i]!.toLowerCase()) break;
    i += 1;
  }
  return i;
}

/** Words shared at end of `a` and start of `b`. */
export function suffixPrefixOverlapWords(a: string, b: string): number {
  const aWords = a.trim().split(/\s+/).filter(Boolean);
  const bWords = b.trim().split(/\s+/).filter(Boolean);
  const max = Math.min(aWords.length, bWords.length, 80);
  for (let size = max; size > 0; size--) {
    const tail = aWords.slice(-size).map((w) => w.toLowerCase());
    const head = bWords.slice(0, size).map((w) => w.toLowerCase());
    if (tail.every((w, i) => w === head[i])) return size;
  }
  return 0;
}

/**
 * Merge within one browser recognition session (cumulative finals — same utterance).
 */
export function absorbSessionFinal(accumulated: string, incoming: string): string {
  const prior = accumulated.trim().replace(/\s+/g, " ");
  const next = incoming.trim().replace(/\s+/g, " ");
  if (!next) return prior;
  if (!prior) return next;

  const priorNorm = normalizeTranscript(prior);
  const nextNorm = normalizeTranscript(next);

  if (nextNorm === priorNorm) return prior;
  if (nextNorm.startsWith(priorNorm)) return next;
  if (priorNorm.startsWith(nextNorm)) return prior;

  return `${prior} ${next}`;
}

/**
 * Append a new utterance after recognition restarts (do not treat shared prefix as duplicate).
 */
export function appendUtterance(accumulated: string, utterance: string): string {
  const prior = accumulated.trim().replace(/\s+/g, " ");
  const next = utterance.trim().replace(/\s+/g, " ");
  if (!next) return prior;
  if (!prior) return next;

  const priorNorm = normalizeTranscript(prior);
  const nextNorm = normalizeTranscript(next);

  if (nextNorm === priorNorm) return prior;
  if (priorNorm.startsWith(nextNorm)) return prior;
  if (nextNorm.startsWith(priorNorm)) return next;

  const overlap = suffixPrefixOverlapWords(prior, next);
  if (overlap > 0) {
    const nextWords = next.split(/\s+/).filter(Boolean);
    const tail = nextWords.slice(overlap).join(" ");
    return tail ? `${prior} ${tail}`.trim() : prior;
  }

  if (prior.includes(next) && next.length < prior.length) return prior;
  if (next.includes(prior)) return next;

  return `${prior} ${next}`;
}

/** @deprecated Prefer absorbSessionFinal + appendUtterance */
export function absorbSpeechResult(accumulated: string, incoming: string): string {
  return appendUtterance(accumulated, incoming);
}

export function mergeSpeechChunk(accumulated: string, chunk: string): string {
  return appendUtterance(accumulated, chunk);
}

/** Remove consecutive duplicate word blocks only (not distinct continued speech). */
export function collapseRepeatedPhrases(text: string, minBlockWords = 12): string {
  let words = text.trim().split(/\s+/).filter(Boolean);
  if (words.length < minBlockWords * 2) return text.trim();

  let changed = true;
  while (changed && words.length >= minBlockWords * 2) {
    changed = false;
    const maxSize = Math.min(Math.floor(words.length / 2), 120);
    for (let size = maxSize; size >= minBlockWords; size--) {
      for (let i = 0; i + size * 2 <= words.length; i++) {
        const block = words.slice(i, i + size);
        const next = words.slice(i + size, i + size * 2);
        const same = block.every((w, idx) => w.toLowerCase() === next[idx]?.toLowerCase());
        if (same) {
          words = [...words.slice(0, i + size), ...words.slice(i + size * 2)];
          changed = true;
          break;
        }
      }
      if (changed) break;
    }
  }

  return words.join(" ").replace(/\s+/g, " ").trim();
}

export function joinSpeechSegments(segments: string[]): string {
  return collapseRepeatedPhrases(
    segments.reduce((acc, seg) => appendUtterance(acc, seg), ""),
  );
}

export function pickBestTranscript(...candidates: (string | undefined | null)[]): string {
  let best = "";
  for (const raw of candidates) {
    const t = (raw ?? "").trim().replace(/\s+/g, " ");
    if (t.length > best.length) best = t;
  }
  return collapseRepeatedPhrases(best);
}

export function mergeTranscriptSegments(
  previous: string | null | undefined,
  newSegment: string | null | undefined,
): string {
  return collapseRepeatedPhrases(
    appendUtterance((previous ?? "").trim(), (newSegment ?? "").trim()),
  );
}

export function appendUniqueSpeechSegment(segments: string[], segment: string): string[] {
  const merged = joinSpeechSegments([...segments, segment]);
  return merged ? [merged] : [];
}
