import { ReactNode } from "react";

export function Card({
  title,
  children,
  className = "",
}: {
  title: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`glass-panel p-5 ${className}`}>
      <h2 className="mb-4 text-xs font-semibold uppercase text-white/42">{title}</h2>
      {children}
    </section>
  );
}
