"use client";

import { ClerkProvider } from "@clerk/nextjs";

export function AppClerkProvider({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider
      appearance={{
        variables: {
          colorPrimary: "hsl(211 100% 52%)",
          colorBackground: "hsl(240 2% 11%)",
          colorInputBackground: "hsl(240 2% 17%)",
          colorText: "hsl(0 0% 98%)",
        },
      }}
    >
      {children}
    </ClerkProvider>
  );
}
