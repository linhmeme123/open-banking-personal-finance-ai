"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bot,
  ChartNoAxesCombined,
  CreditCard,
  Landmark,
  LayoutDashboard,
  PiggyBank,
  ReceiptText,
  ScrollText,
  UserRound,
  X,
} from "lucide-react";
import { Brand } from "@/components/Brand";

const items = [
  { href: "/app", label: "Overview", icon: LayoutDashboard },
  { href: "/app/accounts", label: "Accounts", icon: CreditCard },
  { href: "/app/transactions", label: "Transactions", icon: ReceiptText },
  { href: "/app/insights", label: "Insights", icon: ChartNoAxesCombined },
  { href: "/app/open-banking", label: "Connect banks", icon: Landmark },
  { href: "/app/ai", label: "AI Coach", icon: Bot },
  { href: "/app/consents", label: "Consents", icon: ScrollText },
  { href: "/app/budgets", label: "Budgets", icon: PiggyBank },
  { href: "/app/profile", label: "Profile", icon: UserRound },
];

type SidebarProps = {
  open: boolean;
  onClose: () => void;
};

export function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {open && (
        <button
          aria-label="Close navigation"
          className="fixed inset-0 z-30 bg-black/65 lg:hidden"
          onClick={onClose}
          type="button"
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-white/[0.08] bg-[#0b090e]/95 px-3 py-5 backdrop-blur-xl transition-transform lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-2">
          <Brand href="/app" />
          <button
            aria-label="Close navigation"
            className="rounded-md p-1.5 text-white/45 hover:bg-white/[0.06] hover:text-white lg:hidden"
            onClick={onClose}
            type="button"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>

        <nav className="mt-10 grid gap-1">
          {items.map((item) => {
            const active =
              item.href === "/app" ? pathname === item.href : pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <Link
                className={`flex h-10 items-center gap-3 rounded-md px-3 text-sm font-medium transition ${
                  active
                    ? "bg-gradient-to-r from-pink-500/25 to-fuchsia-500/10 text-pink-100 shadow-[inset_2px_0_0_#f472b6]"
                    : "text-white/48 hover:bg-white/[0.05] hover:text-white/85"
                }`}
                href={item.href}
                key={item.href}
                onClick={onClose}
              >
                <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto rounded-lg border border-pink-300/10 bg-pink-300/[0.035] p-3">
          <p className="text-xs font-semibold text-pink-200">AI finance layer</p>
          <p className="mt-1 text-xs leading-5 text-white/38">
            Your synced banking data powers every insight.
          </p>
        </div>
      </aside>
    </>
  );
}
