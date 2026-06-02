"use client";

import { useState } from "react";
import { FileText, ThumbsDown, ThumbsUp } from "lucide-react";
import type { MessageOut } from "@/lib/types";

type Props = { message: MessageOut };

function HighlightedText({ text }: { text: string }) {
  // Simple heuristic: highlight sequences of capitalized words that end with "Fund"
  const parts = text.split(/(HDFC Flexi Cap Fund|HDFC [A-Za-z]+ Fund|[A-Z][a-z]+ [A-Za-z]+ Fund)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (/[A-Z][a-z]+ [A-Za-z]+ Fund/.test(part)) {
          return (
            <span key={i} className="font-semibold text-emerald-400">
              {part}
            </span>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);

  const time = message.created_at
    ? new Date(message.created_at).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  if (isUser) {
    return (
      <div className="flex flex-col items-end gap-1">
        <article className="max-w-[min(85%,36rem)] rounded-3xl bg-emerald-500 px-5 py-3 text-sm text-zinc-950 shadow-md">
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        </article>
        {time && <span className="mr-2 text-[0.65rem] text-zinc-600">{time}</span>}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-start gap-3">
      <article className="max-w-[min(92%,42rem)] rounded-2xl border border-zinc-800/60 bg-zinc-900/50 px-5 py-4 text-sm leading-relaxed text-zinc-200 shadow-sm">
        <p className="whitespace-pre-wrap">
          <HighlightedText text={message.content} />
        </p>
      </article>

      {/* Source card */}
      <div className="max-w-[min(92%,42rem)] rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-4">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 rounded-lg bg-emerald-500/10 p-1.5 text-emerald-400">
            <FileText className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-semibold text-zinc-200">
              Source: Scheme Information Document (SID)
            </p>
            <p className="mt-0.5 text-xs text-zinc-500">
              Page 42 • Updated June 2025
            </p>
          </div>
        </div>
        <button
          type="button"
          className="mt-3 w-full rounded-xl bg-zinc-800/60 py-2 text-xs font-semibold text-zinc-300 transition hover:bg-zinc-800"
        >
          View Official Document
        </button>
      </div>

      {/* Feedback */}
      <div className="flex items-center gap-3 pl-1">
        <span className="text-xs italic text-zinc-500">Was this helpful?</span>
        <button
          type="button"
          onClick={() => setFeedback("up")}
          className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs transition ${
            feedback === "up"
              ? "border-emerald-500/40 bg-emerald-950/20 text-emerald-300"
              : "border-zinc-700/60 bg-zinc-900/40 text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-300"
          }`}
        >
          <ThumbsUp className="h-3.5 w-3.5" />
          Helpful
        </button>
        <button
          type="button"
          onClick={() => setFeedback("down")}
          className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs transition ${
            feedback === "down"
              ? "border-rose-500/40 bg-rose-950/20 text-rose-300"
              : "border-zinc-700/60 bg-zinc-900/40 text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-300"
          }`}
        >
          <ThumbsDown className="h-3.5 w-3.5" />
          Not Helpful
        </button>
      </div>
    </div>
  );
}
