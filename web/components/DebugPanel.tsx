"use client";

type Props = {
  data: Record<string, unknown> | null;
  onClose: () => void;
};

export function DebugPanel({ data, onClose }: Props) {
  if (!data) return null;
  return (
    <section
      className="border-t border-zinc-800 bg-zinc-950/90 px-4 py-3"
      aria-label="API debug"
    >
      <div className="mb-2 flex items-center justify-between gap-2">
        <h2 className="text-[0.65rem] font-semibold uppercase tracking-wider text-zinc-500">
          Last response (debug)
        </h2>
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg px-2 py-1 text-xs text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300"
        >
          Dismiss
        </button>
      </div>
      <pre className="scrollbar-thin max-h-48 overflow-auto rounded-lg border border-zinc-800/80 bg-black/40 p-3 font-mono text-[0.7rem] leading-relaxed text-zinc-400">
        {JSON.stringify(data, null, 2)}
      </pre>
    </section>
  );
}
