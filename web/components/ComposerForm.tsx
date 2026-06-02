"use client";

import { useState, type FormEvent } from "react";
import { Send } from "lucide-react";

type Props = {
  onSend: (text: string) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
};

export function ComposerForm({
  onSend,
  disabled,
  placeholder = "Ask about Axis Bluechip, Quant Small Cap, etc…",
}: Props) {
  const [value, setValue] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const text = value.trim();
    if (!text || disabled) return;
    setValue("");
    await onSend(text);
  }

  return (
    <form onSubmit={handleSubmit} className="px-2 pb-2 pt-1">
      <div className="flex items-end gap-2 rounded-3xl border border-zinc-700/60 bg-zinc-900/60 px-4 py-3 backdrop-blur-sm">
        <label htmlFor="chat-input" className="sr-only">
          Message
        </label>
        <textarea
          id="chat-input"
          name="message"
          rows={1}
          maxLength={16000}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={disabled}
          placeholder={placeholder}
          className="max-h-32 flex-1 resize-none bg-transparent px-1 py-1.5 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none disabled:opacity-50"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="mb-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-zinc-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </form>
  );
}
