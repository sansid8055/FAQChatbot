"use client";

import {
  Bookmark,
  Clock,
  HelpCircle,
  LayoutDashboard,
  MessageSquarePlus,
  Settings,
  TrendingUp,
} from "lucide-react";
import type { ThreadOut } from "@/lib/types";

type Props = {
  threads: ThreadOut[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  busy?: boolean;
};

const NAV_ITEMS = [
  { icon: MessageSquarePlus, label: "New Conversation" },
  { icon: TrendingUp, label: "Market Trends" },
  { icon: LayoutDashboard, label: "Portfolio Link" },
  { icon: Bookmark, label: "Saved Queries" },
];

export function ThreadRail({ threads, activeId, onSelect, onNew, busy }: Props) {
  return (
    <aside className="flex min-h-0 flex-col gap-5 py-2">
      <div className="px-1">
        <h2 className="text-xl font-bold text-zinc-100">MF Assistant</h2>
        <p className="mt-0.5 text-xs text-zinc-500">AI Research Engine</p>
      </div>

      <button
        type="button"
        onClick={onNew}
        disabled={busy}
        className="rounded-full bg-emerald-500 px-5 py-3 text-sm font-semibold text-zinc-950 shadow-lg shadow-emerald-900/20 transition hover:bg-emerald-400 disabled:opacity-50"
      >
        + New Conversation
      </button>

      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = item.label === "New Conversation" && !activeId && threads.length === 0;
          return (
            <button
              key={item.label}
              type="button"
              onClick={() => {
                if (item.label === "New Conversation") onNew();
              }}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition ${
                isActive
                  ? "bg-zinc-800/80 text-emerald-400"
                  : "text-zinc-400 hover:bg-zinc-800/40 hover:text-zinc-200"
              }`}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="min-h-0 flex-1 overflow-hidden">
        {threads.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-zinc-600">
            <Clock className="h-5 w-5" />
            <p className="text-xs">No recent threads</p>
          </div>
        ) : (
          <ul className="scrollbar-thin max-h-[min(40vh,22rem)] overflow-y-auto pr-1">
            {threads.map((t) => {
              const active = t.id === activeId;
              return (
                <li key={t.id}>
                  <button
                    type="button"
                    onClick={() => onSelect(t.id)}
                    className={`flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm transition ${
                      active
                        ? "bg-zinc-800/80 text-emerald-400"
                        : "text-zinc-400 hover:bg-zinc-800/40 hover:text-zinc-200"
                    }`}
                  >
                    <MessageSquarePlus className="h-4 w-4 shrink-0" />
                    <span className="block truncate">
                      {t.id.slice(0, 8)}…
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <div className="flex flex-col gap-1 border-t border-zinc-800/60 pt-3">
        <button
          type="button"
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm text-zinc-400 transition hover:bg-zinc-800/40 hover:text-zinc-200"
        >
          <Settings className="h-4 w-4" />
          Settings
        </button>
        <button
          type="button"
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm text-zinc-400 transition hover:bg-zinc-800/40 hover:text-zinc-200"
        >
          <HelpCircle className="h-4 w-4" />
          Help Center
        </button>
      </div>
    </aside>
  );
}
