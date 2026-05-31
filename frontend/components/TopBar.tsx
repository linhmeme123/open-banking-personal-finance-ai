"use client";

import { Bell, Menu } from "lucide-react";
import { usePathname } from "next/navigation";
import { ProfileMenu } from "@/components/ProfileMenu";

const titles: Record<string, string> = {
  "/app": "Overview",
  "/app/accounts": "Accounts",
  "/app/transactions": "Transactions",
  "/app/insights": "Insights",
  "/app/open-banking": "Open Banking",
  "/app/ai": "AI Coach",
  "/app/consents": "Consents",
  "/app/budgets": "Budgets",
  "/app/profile": "Profile",
};

export function TopBar({ onOpenSidebar }: { onOpenSidebar: () => void }) {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/[0.08] bg-[#08070b]/75 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
      <div className="flex items-center gap-3">
        <button
          aria-label="Open navigation"
          className="rounded-md p-2 text-white/60 transition hover:bg-white/[0.06] hover:text-white lg:hidden"
          onClick={onOpenSidebar}
          type="button"
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </button>
        <h1 className="text-base font-semibold text-white">{titles[pathname] ?? "Velora"}</h1>
      </div>
      <div className="flex items-center gap-3">
        <button
          aria-label="Notifications"
          className="rounded-md p-2 text-white/45 transition hover:bg-white/[0.06] hover:text-white"
          title="Notifications"
          type="button"
        >
          <Bell className="h-4 w-4" aria-hidden="true" />
        </button>
        <ProfileMenu />
      </div>
    </header>
  );
}
