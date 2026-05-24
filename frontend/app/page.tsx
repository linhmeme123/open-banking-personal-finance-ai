"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { DemoSession, demoLogin, getStoredSession } from "@/lib/session";

type Account = {
  id: number;
  account_name: string;
  balance: number;
  currency: string;
  provider_name: string;
};

export default function HomePage() {
  const [session, setSession] = useState<DemoSession | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stored = getStoredSession();
    setSession(stored);
    if (stored) {
      apiGet<Account[]>("/api/accounts", stored.access_token)
        .then(setAccounts)
        .catch(() => setAccounts([]));
    }
  }, []);

  async function signIn() {
    setLoading(true);
    try {
      const nextSession = await demoLogin();
      setSession(nextSession);
      const nextAccounts = await apiGet<Account[]>("/api/accounts", nextSession.access_token);
      setAccounts(nextAccounts);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6">
      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <div className="grid gap-6 md:grid-cols-[1.4fr_1fr] md:items-center">
          <div>
            <p className="mb-3 text-sm font-semibold uppercase text-slate-500">
              Open Banking Personal Finance AI
            </p>
            <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
              Quản lý dòng tiền cá nhân từ sandbox banking và AI coach.
            </h1>
            <p className="mt-4 max-w-2xl text-slate-600">
              Flow demo gồm đăng nhập, kết nối ngân hàng, consent audit, sync giao dịch,
              dashboard, budget, insight và chat tài chính.
            </p>
          </div>

          <div className="rounded-lg border bg-slate-50 p-4">
            {session ? (
              <div className="grid gap-3">
                <div>
                  <p className="text-sm text-slate-500">Signed in as</p>
                  <p className="font-semibold">{session.user.email}</p>
                </div>
                <p className="text-sm text-slate-600">
                  {accounts.length > 0
                    ? `${accounts.length} account connected`
                    : "No account synced yet"}
                </p>
                <div className="flex flex-wrap gap-2">
                  <Link className="rounded-lg bg-slate-900 px-4 py-2 text-white" href="/connect">
                    Connect bank
                  </Link>
                  <Link className="rounded-lg border bg-white px-4 py-2" href="/dashboard">
                    Dashboard
                  </Link>
                </div>
              </div>
            ) : (
              <div className="grid gap-3">
                <p className="text-sm text-slate-600">Start with the demo banking identity.</p>
                <button
                  className="rounded-lg bg-slate-900 px-4 py-2 text-white disabled:opacity-60"
                  disabled={loading}
                  onClick={signIn}
                >
                  {loading ? "Signing in..." : "Demo sign in"}
                </button>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        {[
          ["Connect", "Choose sandbox provider and grant consent.", "/connect"],
          ["Sync", "Import account and transaction data.", "/connect"],
          ["Analyze", "Review cashflow, budgets, and recurring payments.", "/insights"],
          ["Ask AI", "Chat with answers grounded in your data.", "/chat"],
        ].map(([title, desc, href]) => (
          <Link key={title} href={href} className="rounded-lg border bg-white p-5 shadow-sm hover:border-slate-400">
            <h2 className="font-semibold">{title}</h2>
            <p className="mt-2 text-sm text-slate-600">{desc}</p>
          </Link>
        ))}
      </section>
    </div>
  );
}
