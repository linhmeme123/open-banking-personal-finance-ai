import { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2 className="mt-2 text-2xl font-semibold text-white sm:text-3xl">{title}</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-white/42">{description}</p>
      </div>
      {action}
    </div>
  );
}
