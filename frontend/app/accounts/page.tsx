"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/Card";
import { apiGet } from "@/lib/api";
import { getStoredSession } from "@/lib/session";

type Account = {
  id: number;
  account_name: string;
  account_type: string;
  currency: string;
  balance: number;
  provider_name: string;
};

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);

  useEffect(() => {
    const session = getStoredSession();
    if (!session) return;
    apiGet<Account[]>("/api/accounts", session.access_token)
      .then(setAccounts)
      .catch(() => setAccounts([]));
  }, []);

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">Accounts</h1>
        <p className="mt-2 text-slate-600">Connected sandbox accounts and balances.</p>
      </div>

      <section className="grid gap-4 md:grid-cols-2">
        {accounts.map((account) => (
          <Card key={account.id} title={account.provider_name}>
            <p className="text-lg font-semibold">{account.account_name}</p>
            <p className="mt-1 text-sm text-slate-600">{account.account_type}</p>
            <p className="mt-4 text-2xl font-bold">
              {account.balance.toLocaleString()} {account.currency}
            </p>
          </Card>
        ))}
        {accounts.length === 0 && (
          <div className="rounded-lg border bg-white p-6 text-slate-600 shadow-sm">No connected accounts yet.</div>
        )}
      </section>
    </div>
  );
}
