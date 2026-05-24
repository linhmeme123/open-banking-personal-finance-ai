"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card } from "@/components/Card";
import { apiGet } from "@/lib/api";
import { getStoredSession } from "@/lib/session";

type Summary = {
  income: number;
  expense: number;
  net_cashflow: number;
  category_breakdown: { category: string; amount: number }[];
  budget_status: {
    category: string;
    monthly_limit: number;
    spent: number;
    remaining: number;
  }[];
};

type Recurring = {
  merchant_name: string;
  amount: number;
  currency: string;
  occurrences: number;
};

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [recurring, setRecurring] = useState<Recurring[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const session = getStoredSession();
    if (!session) {
      setLoading(false);
      return;
    }
    Promise.all([
      apiGet<Summary>("/api/insights/monthly-summary", session.access_token),
      apiGet<Recurring[]>("/api/insights/recurring-payments", session.access_token),
    ])
      .then(([nextSummary, nextRecurring]) => {
        setSummary(nextSummary);
        setRecurring(nextRecurring);
      })
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading dashboard...</p>;

  if (!summary) {
    return (
      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="mt-2 text-slate-600">Sign in and sync a sandbox provider to see your finance dashboard.</p>
        <Link className="mt-4 inline-flex rounded-lg bg-slate-900 px-4 py-2 text-white" href="/">
          Start flow
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="mt-2 text-slate-600">Cashflow, budgets, and recurring payments from synced banking data.</p>
      </div>

      <section className="grid gap-4 md:grid-cols-3">
        <Card title="Income">
          <p className="text-2xl font-bold">{summary.income.toLocaleString()} VND</p>
        </Card>
        <Card title="Expense">
          <p className="text-2xl font-bold">{summary.expense.toLocaleString()} VND</p>
        </Card>
        <Card title="Net Cashflow">
          <p className="text-2xl font-bold">{summary.net_cashflow.toLocaleString()} VND</p>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card title="Category Breakdown">
            <div className="grid gap-3">
              {summary.category_breakdown.map((item) => (
                <div key={item.category} className="flex items-center justify-between rounded-lg bg-slate-50 p-3">
                  <span className="font-medium">{item.category}</span>
                  <span>{item.amount.toLocaleString()} VND</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <Card title="Recurring">
          <div className="grid gap-3">
            {recurring.length === 0 && <p className="text-sm text-slate-600">No recurring payments detected.</p>}
            {recurring.map((item) => (
              <div key={`${item.merchant_name}-${item.amount}`} className="rounded-lg bg-slate-50 p-3">
                <p className="font-medium">{item.merchant_name}</p>
                <p className="text-sm text-slate-600">
                  {item.amount.toLocaleString()} {item.currency} x {item.occurrences}
                </p>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <Card title="Budget Status">
        <div className="grid gap-3 md:grid-cols-2">
          {summary.budget_status.length === 0 && <p className="text-sm text-slate-600">No budgets yet.</p>}
          {summary.budget_status.map((item) => (
            <div key={item.category} className="rounded-lg bg-slate-50 p-3">
              <div className="flex justify-between gap-3">
                <span className="font-medium">{item.category}</span>
                <span>{item.spent.toLocaleString()} / {item.monthly_limit.toLocaleString()} VND</span>
              </div>
              <div className="mt-2 h-2 rounded bg-slate-200">
                <div
                  className="h-2 rounded bg-emerald-600"
                  style={{ width: `${Math.min(100, (item.spent / item.monthly_limit) * 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
