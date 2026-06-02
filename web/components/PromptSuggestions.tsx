"use client";

type Props = {
  onPick: (text: string) => void;
  disabled?: boolean;
};

const EXAMPLES = [
  "What is the minimum SIP amount?",
  "What is the expense ratio?",
  "What are the risk factors?",
];

export function PromptSuggestions({ onPick, disabled }: Props) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-3">
      {EXAMPLES.map((q) => (
        <button
          key={q}
          type="button"
          disabled={disabled}
          onClick={() => onPick(q)}
          className="rounded-full border border-zinc-700/80 bg-zinc-900/60 px-4 py-2 text-left text-sm text-zinc-300 transition hover:border-emerald-500/40 hover:bg-emerald-950/20 hover:text-emerald-100 disabled:opacity-40"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
