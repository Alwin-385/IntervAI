"use client";

import { SignedIn, SignedOut, SignInButton, SignUpButton } from "@clerk/nextjs";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";

export function HeroCta() {
  return (
    <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
      <SignedOut>
        <SignUpButton mode="redirect" forceRedirectUrl="/dashboard">
          <Button size="lg" className="gap-2 px-8">
            Get started
            <ArrowRight className="h-4 w-4" />
          </Button>
        </SignUpButton>
        <SignInButton mode="redirect" forceRedirectUrl="/dashboard">
          <Button size="lg" variant="outline">
            Log in
          </Button>
        </SignInButton>
      </SignedOut>
      <SignedIn>
        <Button size="lg" className="gap-2 px-8" asChild>
          <Link href="/dashboard">
            Go to dashboard
            <ArrowRight className="h-4 w-4" />
          </Link>
        </Button>
      </SignedIn>
    </div>
  );
}
