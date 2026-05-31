"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { LogOut, UserRound } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/components/AuthProvider";
import { UserAvatar } from "@/components/UserAvatar";

export function ProfileMenu() {
  const router = useRouter();
  const { logout, status, user } = useAuth();
  const [open, setOpen] = useState(false);

  async function signOut() {
    await logout();
    router.replace("/");
  }

  return (
    <div className="relative">
      <button
        aria-expanded={open}
        aria-label="Open profile menu"
        className="rounded-full outline-none ring-pink-400/40 transition hover:ring-2"
        onClick={() => setOpen((current) => !current)}
        type="button"
      >
        <UserAvatar name={user?.full_name} size="sm" />
      </button>

      {open && (
        <div className="glass-panel absolute right-0 top-12 z-50 w-56 p-2">
          <div className="border-b border-white/[0.08] px-3 py-2">
            <p className="truncate text-sm font-semibold text-white">{user?.full_name}</p>
            <p className="truncate text-xs text-white/45">{user?.email}</p>
          </div>
          <Link
            className="mt-1 flex items-center gap-2 rounded-md px-3 py-2 text-sm text-white/70 transition hover:bg-white/[0.07] hover:text-white"
            href="/app/profile"
            onClick={() => setOpen(false)}
          >
            <UserRound className="h-4 w-4" aria-hidden="true" />
            Profile
          </Link>
          <button
            className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-white/70 transition hover:bg-white/[0.07] hover:text-white disabled:opacity-50"
            disabled={status === "loading"}
            onClick={signOut}
            type="button"
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
            Log out
          </button>
        </div>
      )}
    </div>
  );
}
