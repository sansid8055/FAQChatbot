"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { apiJson, getApiBase } from "@/lib/api";
import type { MessageOut, PostMessageResponse, ThreadOut } from "@/lib/types";
import { ChatMainPanel } from "@/components/ChatMainPanel";
import { SchemeSnapshot } from "@/components/SchemeSnapshot";
import { ThreadRail } from "@/components/ThreadRail";
import { Toast } from "@/components/Toast";

function threadIdFromHash(): string | null {
  if (typeof window === "undefined") return null;
  const h = window.location.hash.replace(/^#/, "").trim();
  return /^[0-9a-f-]{36}$/i.test(h) ? h : null;
}

export function ChatApp() {
  const [threads, setThreads] = useState<ThreadOut[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageOut[]>([]);
  const [toast, setToast] = useState<string | null>(null);
  const [debug, setDebug] = useState<Record<string, unknown> | null>(null);
  const [sending, setSending] = useState(false);
  const activeRef = useRef<string | null>(null);
  activeRef.current = activeThreadId;

  const showError = useCallback((msg: string) => {
    setToast(msg);
    window.setTimeout(() => setToast(null), 5200);
  }, []);

  const loadThreads = useCallback(async () => {
    if (!getApiBase()) return [];
    try {
      const list = await apiJson<ThreadOut[]>("/threads");
      setThreads(list);
      return list;
    } catch (e) {
      showError(e instanceof Error ? e.message : String(e));
      return [];
    }
  }, [showError]);

  const selectThread = useCallback(
    async (id: string) => {
      if (!getApiBase()) return;
      setActiveThreadId(id);
      window.history.replaceState(null, "", `#${id}`);
      try {
        const data = await apiJson<{ messages: MessageOut[] }>(
          `/threads/${encodeURIComponent(id)}/messages`,
        );
        setMessages(data.messages ?? []);
        await loadThreads();
      } catch (e) {
        showError(e instanceof Error ? e.message : String(e));
      }
    },
    [loadThreads, showError],
  );

  const createThread = useCallback(async () => {
    if (!getApiBase()) return;
    try {
      const t = await apiJson<ThreadOut>("/threads", {
        method: "POST",
        body: JSON.stringify({}),
      });
      setActiveThreadId(t.id);
      window.history.replaceState(null, "", `#${t.id}`);
      setMessages([]);
      await loadThreads();
    } catch (e) {
      showError(e instanceof Error ? e.message : String(e));
    }
  }, [loadThreads, showError]);

  useEffect(() => {
    if (!getApiBase()) return;
    let cancelled = false;
    void (async () => {
      const list = await loadThreads();
      if (cancelled) return;
      const fromHash = threadIdFromHash();
      if (fromHash) {
        try {
          await selectThread(fromHash);
          return;
        } catch {
          /* fall through */
        }
      }
      const first = list?.[0];
      if (first) await selectThread(first.id);
    })();
    return () => {
      cancelled = true;
    };
    // Intentionally run once on mount to hydrate threads + optional hash thread.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      const tid = activeRef.current;
      if (!tid || !getApiBase()) return;
      setSending(true);
      setDebug(null);
      try {
        const data = await apiJson<PostMessageResponse>(
          `/threads/${encodeURIComponent(tid)}/messages`,
          {
            method: "POST",
            body: JSON.stringify({ content: text, expand_for_retrieval: true }),
          },
        );
        if (data.debug) setDebug(data.debug as Record<string, unknown>);
        if (activeRef.current === tid) {
          const sel = await apiJson<{ messages: MessageOut[] }>(
            `/threads/${encodeURIComponent(tid)}/messages`,
          );
          setMessages(sel.messages ?? []);
        }
      } catch (e) {
        showError(e instanceof Error ? e.message : String(e));
      } finally {
        setSending(false);
      }
    },
    [showError],
  );

  if (!getApiBase()) {
    return (
      <div className="mx-auto flex max-w-3xl flex-1 items-center justify-center rounded-2xl border border-dashed border-zinc-700/60 bg-zinc-900/30 p-12 text-center text-sm leading-relaxed text-zinc-500">
        Set{" "}
        <code className="mx-1 rounded bg-zinc-800 px-1.5 py-0.5 font-mono text-zinc-300">
          NEXT_PUBLIC_API_URL
        </code>{" "}
        in{" "}
        <code className="mx-1 rounded bg-zinc-800 px-1.5 py-0.5 font-mono text-zinc-300">
          web/.env.local
        </code>{" "}
        to enable chat (see banner above).
      </div>
    );
  }

  const hasMessages = messages.length > 0;

  return (
    <>
      <div
        className={`mx-auto grid min-h-0 w-full max-w-7xl flex-1 gap-5 ${
          hasMessages
            ? "md:grid-cols-[240px_1fr_280px]"
            : "md:grid-cols-[240px_1fr]"
        }`}
      >
        <ThreadRail
          threads={threads}
          activeId={activeThreadId}
          onSelect={(id) => void selectThread(id)}
          onNew={() => void createThread()}
          busy={sending}
        />
        <ChatMainPanel
          threadLabel={activeThreadId}
          messages={messages}
          debug={debug}
          onDismissDebug={() => setDebug(null)}
          onSend={sendMessage}
          sending={sending}
          composerDisabled={!activeThreadId}
        />
        {hasMessages && <SchemeSnapshot />}
      </div>
      <Toast message={toast} />
    </>
  );
}
