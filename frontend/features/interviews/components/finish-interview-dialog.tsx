"use client";

import { Loader2, Flag } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";

interface FinishInterviewDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isPending: boolean;
  answeredCount: number;
  totalQuestions: number;
}

export function FinishInterviewDialog({
  open,
  onClose,
  onConfirm,
  isPending,
  answeredCount,
  totalQuestions,
}: FinishInterviewDialogProps) {
  const unanswered = Math.max(0, totalQuestions - answeredCount);

  return (
    <Dialog
      open={open}
      onClose={() => !isPending && onClose()}
      title="Finish interview early?"
      description="You can complete the session before visiting every question."
    >
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          You have answered <strong className="text-foreground">{answeredCount}</strong> of{" "}
          <strong className="text-foreground">{totalQuestions}</strong> questions.
          {unanswered > 0 ? (
            <>
              {" "}
              <strong className="text-amber-400">{unanswered}</strong> question
              {unanswered === 1 ? "" : "s"} will remain without an answer.
            </>
          ) : (
            " All questions have a saved answer."
          )}
        </p>
        <p className="text-sm text-muted-foreground">
          Your current question will be saved as a draft before the interview is marked complete.
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={isPending}>
            Keep going
          </Button>
          <Button onClick={onConfirm} disabled={isPending} className="gap-2">
            {isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Finishing…
              </>
            ) : (
              <>
                <Flag className="h-4 w-4" />
                Finish interview
              </>
            )}
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
