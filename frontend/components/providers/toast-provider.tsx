"use client";

import { Toaster } from "sonner";

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      richColors
      closeButton
      toastOptions={{
        className: "border border-border/60 bg-card text-foreground",
      }}
    />
  );
}
