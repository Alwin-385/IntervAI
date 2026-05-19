"use client";

import { SignedIn, SignedOut, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";
import Link from "next/link";
import { LayoutDashboard } from "lucide-react";

import { Button } from "@/components/ui/button";

export function UserNav() {
  return (
    <nav className="flex items-center gap-3">
      <SignedOut>
        <SignInButton mode="modal">
          <Button variant="ghost" size="sm">
            Log in
          </Button>
        </SignInButton>
        <SignUpButton mode="modal">
          <Button size="sm">Sign up</Button>
        </SignUpButton>
      </SignedOut>
      <SignedIn>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/dashboard" className="gap-2">
            <LayoutDashboard className="h-4 w-4" />
            Dashboard
          </Link>
        </Button>
        <UserButton
          afterSignOutUrl="/"
          appearance={{
            elements: {
              avatarBox: "h-9 w-9 ring-2 ring-primary/30",
            },
          }}
        />
      </SignedIn>
    </nav>
  );
}
