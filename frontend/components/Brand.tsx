import Link from "next/link";
import { Sparkles } from "lucide-react";

export function Brand({ href = "/", title = "Velora" }: { href?: string; title?: string }) {
  return (
    <Link className="inline-flex items-center gap-3" href={href}>
      <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-pink-400 via-rose-500 to-fuchsia-700 shadow-[0_8px_24px_rgba(236,72,153,0.28)]">
        <Sparkles className="h-4 w-4 text-white" aria-hidden="true" />
      </span>
      <span>
        <span className="block text-sm font-bold text-white">{title}</span>
        <span className="block text-[10px] font-semibold uppercase text-white/40">
          Personal finance AI
        </span>
      </span>
    </Link>
  );
}
