"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Loader2, Mic, Square, Upload } from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { AudioWaveform } from "@/features/speech/components/audio-waveform";
import { TranscriptEditor } from "@/features/speech/components/transcript-editor";
import { transcribeAudio } from "@/features/speech/api";
import { useSpeechCapabilities } from "@/features/speech/hooks/use-speech-capabilities";
import {
  type BrowserSpeechRecognizer,
  createBrowserSpeechRecognizer,
  getSpeechRecognition,
} from "@/features/speech/utils/browser-speech";
import {
  absorbSessionFinal,
  appendUtterance,
  collapseRepeatedPhrases,
  mergeTranscriptSegments,
  pickBestTranscript,
} from "@/features/speech/utils/merge-transcript";
import { cn } from "@/lib/utils";

interface VoiceRecorderProps {
  sessionId: string;
  questionId: string;
  transcript: string;
  audioStoragePath: string | null;
  onTranscriptChange: (text: string) => void;
  onAudioStoragePathChange: (path: string | null) => void;
  onDurationChange?: (seconds: number) => void;
  disabled?: boolean;
}

type RecorderPhase = "idle" | "recording" | "uploading" | "ready";

export function VoiceRecorder({
  sessionId,
  questionId,
  transcript,
  audioStoragePath,
  onTranscriptChange,
  onAudioStoragePathChange,
  onDurationChange,
  disabled = false,
}: VoiceRecorderProps) {
  const { getToken } = useAuth();
  const { data: capabilities } = useSpeechCapabilities();

  const [phase, setPhase] = useState<RecorderPhase>("idle");
  const [levels, setLevels] = useState<number[]>([]);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [uploadProgress, setUploadProgress] = useState(0);
  const utterancesRef = useRef<string[]>([]);
  const currentSessionRef = useRef("");

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const rafRef = useRef<number | null>(null);
  const timerRef = useRef<number | null>(null);
  const recognitionRef = useRef<BrowserSpeechRecognizer | null>(null);
  const recordingStartedRef = useRef<number>(0);
  const transcriptBaseRef = useRef("");
  const phaseRef = useRef<RecorderPhase>("idle");
  const speechSupported = typeof window !== "undefined" && !!getSpeechRecognition();

  useEffect(() => {
    phaseRef.current = phase;
  }, [phase]);

  const rebuildClipTranscript = useCallback((collapse = false) => {
    const parts = [...utterancesRef.current, currentSessionRef.current.trim()].filter(Boolean);
    const joined = parts.reduce((acc, p) => appendUtterance(acc, p), "");
    return collapse ? collapseRepeatedPhrases(joined) : joined;
  }, []);

  const pushCaption = useCallback(
    (text: string, _isFinal: boolean) => {
      const chunk = text.trim().replace(/\s+/g, " ");
      if (!chunk) return;

      // Browser sends the full cumulative text for the current mic session.
      currentSessionRef.current = chunk;

      const clipText = rebuildClipTranscript(false);
      const base = transcriptBaseRef.current;
      const merged = base ? appendUtterance(base, clipText) : clipText;
      onTranscriptChange(merged);
    },
    [onTranscriptChange, rebuildClipTranscript],
  );

  const flushUtteranceSession = useCallback(() => {
    const session = currentSessionRef.current.trim();
    if (session) {
      utterancesRef.current = [...utterancesRef.current, session];
      currentSessionRef.current = "";
    }
    const clipText = rebuildClipTranscript(false);
    if (clipText) {
      const base = transcriptBaseRef.current;
      onTranscriptChange(base ? appendUtterance(base, clipText) : clipText);
    }
  }, [onTranscriptChange, rebuildClipTranscript]);

  const stopVisualizer = useCallback(() => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const cleanupStream = useCallback(() => {
    stopVisualizer();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    audioContextRef.current = null;
    analyserRef.current = null;
  }, [stopVisualizer]);

  useEffect(() => () => cleanupStream(), [cleanupStream]);

  const runVisualizer = useCallback(() => {
    const analyser = analyserRef.current;
    if (!analyser) return;
    const data = new Uint8Array(analyser.frequencyBinCount);

    const tick = () => {
      analyser.getByteFrequencyData(data);
      const slice = 32;
      const step = Math.floor(data.length / slice) || 1;
      const next: number[] = [];
      for (let i = 0; i < slice; i++) {
        const v = data[i * step] / 255;
        next.push(Math.max(0.06, v));
      }
      setLevels(next);
      rafRef.current = requestAnimationFrame(tick);
    };
    tick();
  }, []);

  const startRecording = async () => {
    if (disabled) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];
      recordingStartedRef.current = Date.now();
      setRecordingSeconds(0);
      utterancesRef.current = [];
      currentSessionRef.current = "";
      transcriptBaseRef.current = transcript.trim();
      setPhase("recording");

      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;
      runVisualizer();

      timerRef.current = window.setInterval(() => {
        setRecordingSeconds(Math.floor((Date.now() - recordingStartedRef.current) / 1000));
      }, 1000);

      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";
      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.start(250);

      const recognition = createBrowserSpeechRecognizer({
        onPhrase: (text, isFinal) => pushCaption(text, isFinal),
        onSessionBreak: flushUtteranceSession,
        shouldKeepListening: () => phaseRef.current === "recording",
      });
      if (recognition) {
        recognitionRef.current = recognition;
        recognition.start();
      } else {
        toast.warning(
          "Live captions need Chrome or Edge. You can still record audio and type below.",
        );
      }
    } catch {
      toast.error("Microphone access denied or unavailable.");
    }
  };

  const stopRecording = async () => {
    const recorder = mediaRecorderRef.current;
    if (!recorder || recorder.state === "inactive") return;

    const duration = (Date.now() - recordingStartedRef.current) / 1000;
    onDurationChange?.(duration);

    const recognition = recognitionRef.current;
    if (recognition) {
      await recognition.stop();
      const interim = recognition.getPendingInterim();
      if (interim) {
        currentSessionRef.current = absorbSessionFinal(currentSessionRef.current, interim);
      }
      flushUtteranceSession();
      recognitionRef.current = null;
    }

    await new Promise<void>((resolve) => {
      recorder.onstop = () => resolve();
      recorder.stop();
    });

    cleanupStream();
    setPhase("uploading");
    setUploadProgress(0);

    const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
    const priorTranscript = transcriptBaseRef.current;
    const sessionBrowserTranscript = collapseRepeatedPhrases(
      pickBestTranscript(rebuildClipTranscript(true), transcript.trim()),
    );

    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");

      const result = await transcribeAudio({
        file: blob,
        filename: "recording.webm",
        token,
        sessionId,
        questionId,
        durationSeconds: duration,
        previousTranscript: priorTranscript || undefined,
        browserTranscript: sessionBrowserTranscript || undefined,
        onProgress: setUploadProgress,
      });

      const merged = collapseRepeatedPhrases(
        pickBestTranscript(result.transcript, sessionBrowserTranscript, priorTranscript),
      );
      onTranscriptChange(merged);
      onAudioStoragePathChange(result.audio_storage_path);
      setPhase("ready");
      if (!merged && result.audio_storage_path) {
        toast.success("Recording saved — add or edit your answer text below.");
      } else if (
        merged.length < sessionBrowserTranscript.length * 0.5 &&
        sessionBrowserTranscript.length > 40
      ) {
        onTranscriptChange(sessionBrowserTranscript);
        toast.warning("Used browser transcript — server merge was shorter than expected.");
      } else {
        toast.success(
          merged.length > 0
            ? `Transcript saved (${merged.split(/\s+/).length} words)`
            : "Transcript saved",
        );
      }
    } catch (err) {
      if (sessionBrowserTranscript) {
        onTranscriptChange(mergeTranscriptSegments(priorTranscript, sessionBrowserTranscript));
        onAudioStoragePathChange(null);
        setPhase("ready");
        toast.warning("Audio saved locally in text — upload failed. Save your draft.");
      } else {
        setPhase("idle");
        toast.error(err instanceof Error ? err.message : "Upload or transcription failed");
      }
    }
  };

  const formatRecTime = (s: number) => {
    const m = Math.floor(s / 60)
      .toString()
      .padStart(2, "0");
    const sec = (s % 60).toString().padStart(2, "0");
    return `${m}:${sec}`;
  };

  return (
    <div className="space-y-5">
      <AudioWaveform levels={levels} isActive={phase === "recording"} />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          {phase === "recording" && (
            <motion.span
              className="relative flex h-3 w-3"
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ repeat: Infinity, duration: 1.2 }}
            >
              <span className="absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75" />
              <span className="relative inline-flex h-3 w-3 rounded-full bg-red-500" />
            </motion.span>
          )}
          <span className="text-sm text-muted-foreground">
            {phase === "recording" && (
              <>
                Recording{" "}
                <span className="font-mono text-foreground">{formatRecTime(recordingSeconds)}</span>
              </>
            )}
            {phase === "uploading" && "Saving recording…"}
            {phase === "idle" &&
              (transcript.trim()
                ? "Record again to add more — new speech is appended after your existing text"
                : "Tap the mic to record your answer")}
            {phase === "ready" && (audioStoragePath ? "Recording saved" : "Ready")}
          </span>
        </div>

        <div className="flex gap-2">
          {phase !== "recording" ? (
            <Button
              type="button"
              onClick={startRecording}
              disabled={disabled || phase === "uploading"}
              className="gap-2"
            >
              <Mic className="h-4 w-4" />
              Start recording
            </Button>
          ) : (
            <Button
              type="button"
              variant="destructive"
              onClick={() => void stopRecording()}
              className="gap-2"
            >
              <Square className="h-4 w-4 fill-current" />
              Stop recording
            </Button>
          )}
        </div>
      </div>

      {phase === "recording" && transcript.trim() && (
        <div className="max-h-48 overflow-y-auto rounded-lg border border-border/60 bg-muted/30 px-3 py-2 text-sm text-muted-foreground">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground/80">
            Live caption ({transcript.trim().split(/\s+/).length} words)
          </p>
          <p className="mt-1 whitespace-pre-wrap text-foreground">{transcript}</p>
        </div>
      )}

      {phase === "uploading" && (
        <div className="space-y-2 rounded-lg border border-primary/20 bg-primary/5 p-4">
          <div className="flex items-center gap-2 text-sm">
            <Upload className="h-4 w-4 text-primary" />
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            Saving audio…
          </div>
          <Progress value={uploadProgress} max={100} className="h-2" />
        </div>
      )}

      <div
        className={cn(
          "rounded-lg border border-sky-500/25 bg-sky-500/10 px-3 py-2 text-xs text-sky-100/90",
        )}
      >
        <p className="font-medium text-sky-200/95">Free voice-to-text (browser)</p>
        <p className="mt-1 leading-relaxed">
          {capabilities?.transcription_mode === "whisper"
            ? "Whisper mode: browser captions used as fallback."
            : "Long answers supported — Chrome restarts the mic about every minute; we keep appending. Speak in Chrome or Edge."}
          {!speechSupported &&
            " Use Chrome or Edge for live captions, or type your answer manually."}
        </p>
      </div>

      <TranscriptEditor
        value={transcript}
        onChange={onTranscriptChange}
        disabled={disabled || phase === "uploading"}
      />
    </div>
  );
}
