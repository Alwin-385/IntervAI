import { auth } from "@clerk/nextjs/server";

/**
 * Server-side helper to obtain a Clerk session token for backend API calls.
 */
export async function getServerAuthToken(): Promise<string | null> {
  const session = await auth();
  if (!session.userId) return null;
  return session.getToken();
}
