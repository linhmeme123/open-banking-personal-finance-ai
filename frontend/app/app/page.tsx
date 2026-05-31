"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  Bot,
  Landmark,
  PiggyBank,
  RefreshCw,
  TrendingDown,
  TrendingUp,
  WalletCards,
} from "lucide-react";
import { Card } from "@/components/Card";
import { PageHeader } from "@/components/PageHeader";
import { StatCard } from "@/components/StatCard";
import { useAuth } from "@/components/AuthProvider";
import { apiGet } from "@/lib/api";
import { formatCategory, formatCurrency } from "@/lib/format";

type Account = {
  id: number;
  balance: number;
  currency: string;
};

type Transaction = {
  id: number;
  transaction_time: string;
  description: string;
  merchant_name: string | null;
  amount: number;
  currency: string;
  direction: string;
  category: string | null;
};

type Summary = {
  income: number;
  expense: number;
  net_cashflow: number;
  budget_status: {
    category: string;
    monthly_limit: number;
    spent: number;
    remaining: number;
  }[];
};

type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
};

export default function OverviewPage() {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiGet<Account[]>("/api/accounts"),
      apiGet<Transaction[]>("/api/transactions"),
      apiGet<Summary>("/api/insights/monthly-summary"),
      apiGet<ChatMessage[]>("/api/ai/chat/history"),
    ])
      .then(([nextAccounts, nextTransactions, nextSummary, nextHistory]) => {
        setAccounts(nextAccounts);
        setTransactions(nextTransactions);
        setSummary(nextSummary);
        setHistory(nextHistory);
      })
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, []);

  const totalBalance = accounts.reduce((total, account) => total + account.balance, 0);
  const budget = useMemo(() => {
    const totals = summary?.budget_status.reduce(
      (current, item) => ({
        spent: current.spent + item.spent,
        limit: current.limit + item.monthly_limit,
      }),
      { spent: 0, limit: 0 },
    ) ?? { spent: 0, limit: 0 };
    return {
      ...totals,
      percentage: totals.limit ? Math.min(100, Math.round((totals.spent / totals.limit) * 100)) : 0,
    };
  }, [summary]);
  const latestInsight =
    [...history].reverse().find((item) => item.role === "assistant")?.content ||
    (accounts.length
      ? "Your connected data is ready. Ask the AI coach for a personalized read on this month's cashflow."
      : "Connect a bank account to unlock your first AI-powered cashflow insight.");

  return (
    <div className="grid gap-6">
      <PageHeader
        description="Your connected balances, monthly cashflow, and the next signals worth your attention."
        eyebrow="Financial pulse"
        title={`Good to see you, ${user?.full_name.split(" ")[0] ?? "there"}`}
        action={
          <Link className="button-secondary" href="/app/open-banking">
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Sync accounts
          </Link>
        }
      />

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          detail={`${accounts.length} connected ${accounts.length === 1 ? "account" : "accounts"}`}
          icon={WalletCards}
          label="Total balance"
          value={loading ? "Loading..." : formatCurrency(totalBalance)}
        />
        <StatCard
          detail="Current monthly period"
          icon={TrendingUp}
          label="Monthly income"
          tone="cyan"
          value={loading ? "Loading..." : formatCurrency(summary?.income ?? 0)}
        />
        <StatCard
          detail="Current monthly period"
          icon={TrendingDown}
          label="Monthly expense"
          tone="amber"
          value={loading ? "Loading..." : formatCurrency(summary?.expense ?? 0)}
        />
        <StatCard
          detail={budget.limit ? `${formatCurrency(budget.spent)} of ${formatCurrency(budget.limit)}` : "Set your first monthly limit"}
          icon={PiggyBank}
          label="Budget progress"
          tone="violet"
          value={loading ? "Loading..." : `${budget.percentage}%`}
        />
      </section>

      {accounts.length === 0 && !loading && (
        <section className="glass-panel flex flex-wrap items-center justify-between gap-4 border-pink-300/15 bg-pink-300/[0.05] p-5">
          <div>
            <p className="font-semibold text-white">Connect your first banking provider</p>
            <p className="mt-1 text-sm text-white/42">Sync sandbox activity to populate the dashboard.</p>
          </div>
          <Link className="button-primary" href="/app/open-banking">
            <Landmark className="h-4 w-4" aria-hidden="true" />
            Connect bank
          </Link>
        </section>
      )}

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.65fr)_minmax(280px,0.8fr)]">
        <Card title="Recent transactions">
          <div className="grid gap-1">
            {transactions.slice(0, 5).map((transaction) => (
              <div className="flex items-center justify-between gap-4 border-b border-white/[0.07] py-3 last:border-0" key={transaction.id}>
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-white">{transaction.description}</p>
                  <p className="mt-1 text-xs text-white/35">
                    {transaction.category ? formatCategory(transaction.category) : "Uncategorized"} /{" "}
                    {new Date(transaction.transaction_time).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })}
                  </p>
                </div>
                <p className={`shrink-0 text-sm font-semibold ${transaction.direction === "income" ? "text-emerald-300" : "text-white"}`}>
                  {formatCurrency(transaction.amount, transaction.currency)}
                </p>
              </div>
            ))}
            {!transactions.length && (
              <p className="py-6 text-sm text-white/38">No synced transactions yet.</p>
            )}
          </div>
          <Link className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-pink-300 hover:text-pink-200" href="/app/transactions">
            View all transactions
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </Card>

        <Card className="border-pink-300/15 bg-pink-300/[0.045]" title="AI insight">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-pink-300/10 text-pink-200">
            <Bot className="h-5 w-5" aria-hidden="true" />
          </div>
          <p className="mt-4 text-sm leading-7 text-white/68">{latestInsight}</p>
          <Link className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-pink-300 hover:text-pink-200" href="/app/ai">
            Talk to AI Coach
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </Card>
      </section>
    </div>
  );
}
