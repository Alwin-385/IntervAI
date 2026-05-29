"use client";

import { useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";
import { useDeleteInterview } from "@/features/interviews/hooks/use-delete-interview";

interface DeleteInterviewDialogProps {
  sessionId: string;
  sessionTitle: string;
  redirectTo?: string;
  trigger?: ReactNode;
  onDeleted?: () => void;
}

export function DeleteInterviewDialog({
  sessionId,
  sessionTitle,
  redirectTo = "/dashboard/interviews",
  trigger,
  onDeleted,
}: DeleteInterviewDialogProps) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const deleteMutation = useDeleteInterview();

  const handleDelete = () => {
    deleteMutation.mutate(sessionId, {
      onSuccess: () => {
        toast.success("Interview deleted");
        setOpen(false);
        onDeleted?.();
        router.push(redirectTo);
      },
      onError: (err) =>
        toast.error(err instanceof Error ? err.message : "Failed to delete interview"),
    });
  };

  return (
    <>
      {trigger ? (
        <span
          role="presentation"
          onClick={(e) => {
            e.stopPropagation();
            setOpen(true);
          }}
        >
          {trigger}
        </span>
      ) : (
        <Button variant="outline" size="sm" className="gap-2 text-destructive" onClick={() => setOpen(true)}>
          <Trash2 className="h-4 w-4" />
          Delete
        </Button>
      )}

      <Dialog
        open={open}
        onClose={() => !deleteMutation.isPending && setOpen(false)}
        title="Delete interview?"
        description={`This permanently removes "${sessionTitle}" and all generated questions.`}
      >
        <div className="mt-4 flex justify-end gap-2">
          <Button
            variant="outline"
            onClick={() => setOpen(false)}
            disabled={deleteMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            variant="default"
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Deleting…
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4" />
                Delete interview
              </>
            )}
          </Button>
        </div>
      </Dialog>
    </>
  );
}
