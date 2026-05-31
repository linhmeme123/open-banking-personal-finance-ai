import { LucideIcon } from "lucide-react";

export function StatCard({
  icon: Icon,
  label,
  value,
  detail,
  tone = "pink",
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  detail?: string;
  tone?: "pink" | "cyan" | "amber" | "violet";
}) {
  const toneClasses = {
    pink: "bg-pink-400/10 text-pink-300",
    cyan: "bg-cyan-400/10 text-cyan-300",
    amber: "bg-amber-400/10 text-amber-300",
    violet: "bg-violet-400/10 text-violet-300",
  };

  return (
    <section className="glass-panel p-4">
      <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${toneClasses[tone]}`}>
        <Icon className="h-4 w-4" aria-hidden="true" />
      </div>
      <p className="mt-5 text-xs font-medium uppercase text-white/38">{label}</p>
      <p className="mt-2 text-xl font-semibold text-white">{value}</p>
      {detail && <p className="mt-1 text-xs text-white/38">{detail}</p>}
    </section>
  );
}
