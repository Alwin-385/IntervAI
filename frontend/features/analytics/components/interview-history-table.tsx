"use client";

import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { InterviewHistoryItem } from "@/features/analytics/types";

interface Props {
  items: InterviewHistoryItem[];
  page: number;
  pages: number;
  total: number;
  onPageChange: (page: number) => void;
}

export function InterviewHistoryTable({ items, page, pages, total, onPageChange }: Props) {
  return (
    <div className="glass-card rounded-xl border border-border/50 p-4">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold">Interview history</h3>
          <p className="text-xs text-muted-foreground">{total} session(s) total</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-xs text-muted-foreground">
            {page} / {Math.max(pages, 1)}
          </span>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            disabled={page >= pages}
            onClick={() => onPageChange(page + 1)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border/50 text-left text-xs text-muted-foreground">
              <th className="pb-2 pr-4 font-medium">Session</th>
              <th className="pb-2 pr-4 font-medium">Role</th>
              <th className="pb-2 pr-4 font-medium">Type</th>
              <th className="pb-2 pr-4 font-medium">Score</th>
              <th className="pb-2 pr-4 font-medium">Comm.</th>
              <th className="pb-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-muted-foreground">
                  No interviews match these filters.
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.session_id} className="border-b border-border/30 last:border-0">
                  <td className="py-3 pr-4">
                    <Link
                      href={`/dashboard/interviews/${item.session_id}/results`}
                      className="font-medium text-primary hover:underline"
                    >
                      {item.title}
                    </Link>
                    <p className="text-xs text-muted-foreground">
                      {new Date(item.completed_at ?? item.created_at).toLocaleDateString()}
                    </p>
                  </td>
                  <td className="py-3 pr-4 text-muted-foreground">{item.target_role}</td>
                  <td className="py-3 pr-4 capitalize text-muted-foreground">
                    {item.category.replace(/_/g, " ")}
                  </td>
                  <td className="py-3 pr-4 font-semibold">
                    {item.average_score != null ? `${item.average_score}%` : "—"}
                  </td>
                  <td className="py-3 pr-4 text-muted-foreground">
                    {item.communication_score != null ? `${item.communication_score}%` : "—"}
                  </td>
                  <td className="py-3 capitalize text-muted-foreground">{item.status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
