"use client";

import type { ReactNode } from "react";
import { BarChart3, FileText, Sparkles, Target } from "lucide-react";
import type { MessageOut } from "@/lib/types";
import { ComposerForm } from "@/components/ComposerForm";
import { DebugPanel } from "@/components/DebugPanel";
import { MessageBubble } from "@/components/MessageBubble";
import { PromptSuggestions } from "@/components/PromptSuggestions";

type Props = {
  threadLabel: string | null;
  messages: MessageOut[];
  debug: Record<string, unknown> | null;
  onDismissDebug: () => void;
  onSend: (text: string) => Promise<void>;
  sending: boolean;
  composerDisabled: boolean;
};

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex flex-col gap-2 rounded-2xl border border-zinc-800/40 bg-zinc-900/30 p-4">
      <div className="text-zinc-600">{icon}</div>
      <p className="text-xs font-medium text-zinc-500">{title}</p>
      <p className="text-[0.65rem] text-zinc-600">{description}</p>
    </div>
  );
}

export function ChatMainPanel({
  threadLabel,
  messages,
  debug,
  onDismissDebug,
  onSend,
  sending,
  composerDisabled,
}: Props) {
  const hasMessages = messages.length > 0;

  return (
    <section className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-zinc-800/60 bg-zinc-900/20">
      {hasMessages && (
        <div className="flex items-center gap-3 border-b border-zinc-800/60 px-5 py-3">
          <h2 className="text-sm font-semibold text-zinc-100">
            HDFC Flexi Cap Fund | HDFC Mutual Fund
          </h2>
          <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-950/20 px-2 py-0.5 text-[0.65rem] font-medium text-emerald-400">
            <Sparkles className="h-3 w-3" />
            Verified
          </span>
        </div>
      )}

      <div className="scrollbar-thin flex flex-1 flex-col gap-4 overflow-y-auto p-4">
        {!hasMessages ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-6 py-8">
            <div className="flex h-16 w-16 items-center justify-center rounded-full border border-zinc-700/40 bg-zinc-800/30">
              <FileText className="h-7 w-7 text-emerald-400" />
            </div>
            <div className="text-center">
              <h2 className="text-xl font-semibold text-zinc-100 sm:text-2xl">
                Ask Anything About Your Mutual Fund Scheme
              </h2>
              <p className="mx-auto mt-2 max-w-md text-sm text-zinc-500">
                Get factual answers directly from official scheme information
                documents (SID) and SAI.
              </p>
            </div>
            <PromptSuggestions onPick={(t) => void onSend(t)} disabled={composerDisabled} />
            <div className="mx-auto grid max-w-2xl grid-cols-3 gap-3 pt-4">
              <FeatureCard
                icon={<Sparkles className="h-4 w-4" />}
                title="AI-Powered Insights"
                description="Get instant analysis from official documents"
              />
              <FeatureCard
                icon={<BarChart3 className="h-4 w-4" />}
                title="Source Verification"
                description="Every answer linked to scheme documents"
              />
              <FeatureCard
                icon={<Target className="h-4 w-4" />}
                title="Risk Analysis"
                description="Compare with peer funds instantly"
              />
            </div>
          </div>
        ) : (
          messages.map((m) => <MessageBubble key={`${m.id}-${m.created_at}`} message={m} />)
        )}
      </div>

      <DebugPanel data={debug} onClose={onDismissDebug} />

      <ComposerForm onSend={onSend} disabled={composerDisabled || sending} />
      {hasMessages && (
        <p className="pb-2 text-center text-[0.65rem] text-zinc-600">
          AI-generated financial info may contain errors. Always read the SID before investing.
        </p>
      )}
    </section>
  );
}
