import type { Metadata } from "next";

export const dynamic = "force-dynamic";
import { Geist, Geist_Mono } from "next/font/google";

import { AppClerkProvider } from "@/components/providers/clerk-provider";
import { QueryProvider } from "@/components/providers/query-provider";
import { ToastProvider } from "@/components/providers/toast-provider";
import { env } from "@/lib/env";

import "@/styles/globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: env.appName,
  description:
    "AI-powered interview preparation and evaluation platform for modern hiring.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-screen font-sans antialiased`}
      >
        <AppClerkProvider>
          <QueryProvider>
            {children}
            <ToastProvider />
          </QueryProvider>
        </AppClerkProvider>
      </body>
    </html>
  );
}
