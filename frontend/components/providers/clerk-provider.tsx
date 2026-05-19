"use client";

import { ClerkProvider } from "@clerk/nextjs";

export function AppClerkProvider({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider
      appearance={{
        variables: {
          colorPrimary: "hsl(217 91% 60%)",
          colorBackground: "hsl(222 47% 6%)",
          colorInputBackground: "hsl(217 33% 14%)",
          colorText: "hsl(210 40% 98%)",
        },
      }}
    >
      {children}
    </ClerkProvider>
  );
}
