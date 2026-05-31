"use client";

import { useEffect, useState } from "react";
import { Landmark } from "lucide-react";
import { AccountCard } from "@/components/AccountCard";
import { EmptyState } from "@/components/EmptyState";
import { PageHeader } from "@/components/PageHeader";
import { getApiErrorMessage } from "@/lib/api";
import { formatCurrency } from "@/lib/format";
import { Account, getAccounts } from "@/lib/finance";

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    getAccounts()
      .then(setAccounts)
      .catch((error) => setMessage(getApiErrorMessage(error, "Unable to load accounts.")));
  }, []);

  const groups = Array.from(new Set(accounts.map((account) => account.provider_code))).map((providerCode) => ({
    providerCode,
    providerName: accounts.find((account) => account.provider_code === providerCode)?.provider_name ?? providerCode,
    accounts: accounts.filter((account) => account.provider_code === providerCode),
  }));
  const totalBalance = accounts.reduce((total, account) => total + account.balance, 0);

  return (
    <div className="grid gap-7">
      <PageHeader
        action={accounts.length > 0 && <p className="text-right text-sm text-white/42">Total portfolio<br /><span className="mt-1 inline-block text-xl font-semibold text-white">{formatCurrency(totalBalance)}</span></p>}
        description="Balances grouped by each provider connected through your Open Banking sandbox."
        eyebrow="Connected portfolio"
        title="Accounts"
      />

      {message && <p className="rounded-lg border border-pink-300/15 bg-pink-300/[0.05] px-4 py-3 text-sm text-pink-100">{message}</p>}

      {groups.map((group) => (
        <section className="grid gap-4" key={group.providerCode}>
          <div className="flex items-end justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold text-white">{group.providerName}</h2>
              <p className="mt-1 text-sm text-white/38">{group.accounts.length} linked account{group.accounts.length === 1 ? "" : "s"}</p>
            </div>
            <p className="text-sm font-semibold text-pink-200">{formatCurrency(group.accounts.reduce((total, account) => total + account.balance, 0))}</p>
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {group.accounts.map((account) => <AccountCard account={account} key={account.id} />)}
          </div>
        </section>
      ))}

      {!message && accounts.length === 0 && (
        <EmptyState
          action={{ href: "/app/open-banking", label: "Connect a banking provider" }}
          description="Connect a sandbox provider and run your first sync to import account balances."
          icon={Landmark}
          title="No linked accounts yet"
        />
      )}
    </div>
  );
}
