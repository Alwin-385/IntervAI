/** Web Speech API — free, runs in the browser (Chrome / Edge recommended). */

import { absorbSessionFinal, appendUtterance } from "@/features/speech/utils/merge-transcript";

type SpeechRecognitionCtor = new () => SpeechRecognitionInstance;

interface SpeechRecognitionInstance extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
}

interface SpeechRecognitionEventLike {
  resultIndex: number;
  results: {
    length: number;
    [index: number]: {
      isFinal: boolean;
      [index: number]: { transcript: string };
    };
  };
}

export function getSpeechRecognition(): SpeechRecognitionCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as Window & {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

export interface BrowserSpeechRecognizer {
  start(): void;
  stop(): Promise<void>;
  getPendingInterim(): string;
}

const FLUSH_MS = 1200;

export interface BrowserSpeechCallbacks {
  onPhrase: (text: string, isFinal: boolean) => void;
  /** Fired when Chrome restarts the mic session (~every 60s) — flush prior utterance. */
  onSessionBreak?: () => void;
  shouldKeepListening?: () => boolean;
}

/**
 * Long recordings: Chrome restarts recognition periodically; we track each session separately.
 */
export function createBrowserSpeechRecognizer(
  callbacks: BrowserSpeechCallbacks,
): BrowserSpeechRecognizer | null {
  const { onPhrase, onSessionBreak, shouldKeepListening } = callbacks;
  const Ctor = getSpeechRecognition();
  if (!Ctor) return null;

  const recognition = new Ctor();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  let manualStop = false;
  let pendingInterim = "";
  let flushResolve: (() => void) | null = null;
  let currentSessionText = "";

  const emitFromEvent = (event: SpeechRecognitionEventLike) => {
    let bestFinal = "";
    let bestInterim = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i];
      const chunk = result[0]?.transcript?.trim();
      if (!chunk) continue;

      if (result.isFinal) {
        if (chunk.length >= bestFinal.length) {
          bestFinal = chunk;
        }
      } else if (chunk.length >= bestInterim.length) {
        bestInterim = chunk;
      }
    }

    if (bestFinal) {
      currentSessionText = absorbSessionFinal(currentSessionText, bestFinal);
      onPhrase(currentSessionText, true);
      pendingInterim = "";
    } else if (bestInterim) {
      pendingInterim = bestInterim;
      onPhrase(absorbSessionFinal(currentSessionText, bestInterim), false);
    }
  };

  const flushSessionBreak = () => {
    const pending = pendingInterim.trim();
    if (pending) {
      currentSessionText = absorbSessionFinal(currentSessionText, pending);
      pendingInterim = "";
    }
    if (currentSessionText.trim()) {
      onPhrase(currentSessionText, true);
      onSessionBreak?.();
      currentSessionText = "";
    }
  };

  recognition.onresult = emitFromEvent;

  recognition.onerror = (event) => {
    if (manualStop) return;
    if (event.error === "aborted" || event.error === "no-speech") return;
    flushSessionBreak();
    if (shouldKeepListening?.()) {
      try {
        recognition.start();
      } catch {
        // already running
      }
    }
  };

  recognition.onend = () => {
    if (manualStop) {
      const pending = pendingInterim.trim();
      if (pending) {
        currentSessionText = absorbSessionFinal(currentSessionText, pending);
        onPhrase(currentSessionText, true);
        pendingInterim = "";
      }
      if (currentSessionText.trim()) {
        onSessionBreak?.();
        currentSessionText = "";
      }
      flushResolve?.();
      flushResolve = null;
      return;
    }
    flushSessionBreak();
    if (shouldKeepListening?.()) {
      try {
        recognition.start();
      } catch {
        // already running
      }
    }
  };

  return {
    start() {
      manualStop = false;
      pendingInterim = "";
      currentSessionText = "";
      recognition.start();
    },
    stop() {
      manualStop = true;
      return new Promise<void>((resolve) => {
        flushResolve = resolve;
        recognition.stop();
        window.setTimeout(() => {
          flushResolve?.();
          flushResolve = null;
          resolve();
        }, FLUSH_MS);
      });
    },
    getPendingInterim() {
      return pendingInterim;
    },
  };
}
