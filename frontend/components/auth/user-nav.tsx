"use client";

import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignOutButton,
  SignUpButton,
  UserButton,
} from "@clerk/nextjs";
import Link from "next/link";
import { LayoutDashboard, LogOut } from "lucide-react";

import { Button } from "@/components/ui/button";

export function UserNav({ showSignOutLabel = true }: { showSignOutLabel?: boolean }) {
  return (
    <nav className="flex flex-wrap items-center gap-2 sm:gap-3">
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
        <Button variant="ghost" size="sm" asChild className="hidden sm:inline-flex">
          <Link href="/dashboard" className="gap-2">
            <LayoutDashboard className="h-4 w-4" />
            Dashboard
          </Link>
        </Button>
        {showSignOutLabel && (
          <SignOutButton redirectUrl="/">
            <Button variant="outline" size="sm" className="gap-2 border-border/60">
              <LogOut className="h-4 w-4" />
              <span>Log out</span>
            </Button>
          </SignOutButton>
        )}
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
