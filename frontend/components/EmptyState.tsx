import Link from "next/link";
import { ArrowRight, LucideIcon } from "lucide-react";

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: { href: string; label: string };
}) {
  return (
    <section className="glass-panel px-6 py-10 text-center">
      <span className="mx-auto flex h-11 w-11 items-center justify-center rounded-lg border border-pink-300/15 bg-pink-300/[0.07] text-pink-200">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </span>
      <h3 className="mt-4 text-base font-semibold text-white">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-white/42">{description}</p>
      {action && (
        <Link className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-pink-300 hover:text-pink-200" href={action.href}>
          {action.label}
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </Link>
      )}
    </section>
  );
}
