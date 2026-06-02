export function ApiConfigBanner() {
  const base = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (base) return null;
  return (
    <div
      role="alert"
      className="border-b border-amber-500/40 bg-amber-950/40 px-6 py-3 text-center text-sm text-amber-100"
    >
      Set{" "}
      <code className="rounded bg-zinc-900 px-1.5 py-0.5 font-mono text-amber-200">
        NEXT_PUBLIC_API_URL
      </code>{" "}
      (e.g. <code className="font-mono">http://127.0.0.1:8765</code>) in{" "}
      <code className="font-mono">web/.env.local</code>, then restart{" "}
      <code className="font-mono">npm run dev</code>.
    </div>
  );
}
