import { CircleHelp, ShieldCheck, User } from "lucide-react";

export function HeaderBar() {
  return (
    <header className="border-b border-zinc-800/60 bg-[#0b0f0d]/90 backdrop-blur-md px-6 py-4">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold tracking-tight text-emerald-400 sm:text-3xl">
            Groww
          </h1>
          <span className="hidden items-center gap-1.5 rounded-full border border-zinc-700/60 bg-zinc-800/40 px-3 py-1 text-xs text-zinc-400 sm:inline-flex">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            Answers sourced only from official mutual fund scheme documents
          </span>
        </div>
        <div className="flex items-center gap-3 text-zinc-400">
          <button type="button" className="rounded-lg p-2 hover:bg-zinc-800/60 hover:text-zinc-200">
            <CircleHelp className="h-5 w-5" />
          </button>
          <button type="button" className="rounded-lg p-2 hover:bg-zinc-800/60 hover:text-zinc-200">
            <User className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
