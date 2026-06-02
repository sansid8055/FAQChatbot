"use client";

type Props = {
  message: string | null;
};

export function Toast({ message }: Props) {
  if (!message) return null;
  return (
    <div
      role="status"
      className="fixed bottom-6 left-1/2 z-50 max-w-[min(90vw,28rem)] -translate-x-1/2 rounded-xl border border-red-500/40 bg-zinc-900/95 px-4 py-3 text-center text-sm text-red-100 shadow-2xl backdrop-blur-md"
    >
      {message}
    </div>
  );
}
