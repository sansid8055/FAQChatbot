"use client";

import { BadgeCheck } from "lucide-react";

type Props = {
  fundName?: string;
};

function RiskBar({ level }: { level: number }) {
  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className={`h-3 w-1.5 rounded-sm ${
            i < level ? "bg-emerald-400" : "bg-zinc-700"
          }`}
        />
      ))}
    </div>
  );
}

function PeerRow({ name, value, width }: { name: string; value: string; width: number }) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between text-xs">
        <span className="text-zinc-300">{name}</span>
        <span className="text-emerald-400">{value}</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-zinc-700">
        <div
          className="h-full rounded-full bg-emerald-400"
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}

export function SchemeSnapshot({ fundName }: Props) {
  return (
    <aside className="flex min-h-0 flex-col gap-5 py-2">
      <div className="flex items-center gap-2">
        <h2 className="text-lg font-semibold text-zinc-100">Scheme Snapshot</h2>
        <BadgeCheck className="h-4 w-4 text-emerald-400" />
      </div>

      <div className="flex flex-col gap-4">
        {/* Risk Level */}
        <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-4">
          <p className="text-[0.65rem] font-semibold uppercase tracking-wider text-zinc-500">
            Risk Level
          </p>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-sm font-semibold text-red-400">Very High</span>
            <RiskBar level={4} />
          </div>
        </div>

        {/* Expense Ratio */}
        <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-4">
          <p className="text-[0.65rem] font-semibold uppercase tracking-wider text-zinc-500">
            Expense Ratio
          </p>
          <p className="mt-1 text-2xl font-bold text-zinc-100">1.5%</p>
          <p className="mt-0.5 text-xs text-zinc-500">
            Lower than category average of 1.8%
          </p>
        </div>

        {/* Minimum SIP */}
        <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-4">
          <p className="text-[0.65rem] font-semibold uppercase tracking-wider text-zinc-500">
            Minimum SIP
          </p>
          <p className="mt-1 text-2xl font-bold text-emerald-400">₹100</p>
          <p className="mt-0.5 text-xs text-zinc-500">
            Start your investment journey today
          </p>
        </div>

        {/* Peer Comparison */}
        <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-4">
          <h3 className="text-sm font-semibold text-zinc-100">Peer Comparison</h3>
          <div className="mt-4 flex flex-col gap-4">
            <PeerRow name="Parag Parikh Flexi" value="+18.2%" width={75} />
            <PeerRow name="Quant Flexi Cap" value="+21.4%" width={90} />
          </div>
        </div>
      </div>
    </aside>
  );
}
