"use client";

import { useEffect, useState } from "react";
import { ChartNoAxesCombined, Repeat2 } from "lucide-react";
import { Card } from "@/components/Card";
import { PageHeader } from "@/components/PageHeader";
import { apiGet } from "@/lib/api";
import { formatCategory, formatCurrency } from "@/lib/format";

type Breakdown = { category: string; amount: number };
type Recurring = {
  merchant_name: string;
  amount: number;
  currency: string;
  occurrences: number;
};

export default function InsightsPage() {
  const [breakdown, setBreakdown] = useState<Breakdown[]>([]);
  const [recurring, setRecurring] = useState<Recurring[]>([]);

  useEffect(() => {
    Promise.all([
      apiGet<Breakdown[]>("/api/insights/category-breakdown"),
      apiGet<Recurring[]>("/api/insights/recurring-payments"),
    ])
      .then(([nextBreakdown, nextRecurring]) => {
        setBreakdown(nextBreakdown);
        setRecurring(nextRecurring);
      })
      .catch(() => undefined);
  }, []);

  const totalExpense = breakdown.reduce((total, item) => total + item.amount, 0);

  return (
    <div className="grid gap-6">
      <PageHeader
        description="See where spending concentrates and surface payments that repeat over time."
        eyebrow="Pattern detection"
        title="Insights"
      />

      <section className="grid gap-4 lg:grid-cols-2">
        <Card title="Spending by category">
          <div className="mb-5 flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-pink-300/10 text-pink-200">
              <ChartNoAxesCombined className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-xs text-white/38">Tracked expenses</p>
              <p className="text-lg font-semibold text-white">{formatCurrency(totalExpense)}</p>
            </div>
          </div>
          <div className="grid gap-3">
            {breakdown.map((item) => {
              const width = totalExpense ? Math.max(3, Math.round((item.amount / totalExpense) * 100)) : 0;
              return (
                <div key={item.category}>
                  <div className="flex justify-between gap-3 text-sm">
                    <span className="font-medium text-white/72">{formatCategory(item.category)}</span>
                    <span className="text-white/48">{formatCurrency(item.amount)}</span>
                  </div>
                  <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
                    <div className="h-full rounded-full bg-gradient-to-r from-pink-500 to-fuchsia-400" style={{ width: `${width}%` }} />
                  </div>
                </div>
              );
            })}
            {!breakdown.length && <p className="text-sm text-white/38">Sync transaction data to see category insights.</p>}
          </div>
        </Card>

        <Card title="Recurring payments">
          <div className="grid gap-2">
            {recurring.map((item) => (
              <div className="glass-subtle flex items-center justify-between gap-4 p-3" key={`${item.merchant_name}-${item.amount}`}>
                <div className="flex min-w-0 items-center gap-3">
                  <Repeat2 className="h-4 w-4 shrink-0 text-violet-300" aria-hidden="true" />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-white">{item.merchant_name}</p>
                    <p className="mt-1 text-xs text-white/35">{item.occurrences} detected payments</p>
                  </div>
                </div>
                <p className="shrink-0 text-sm font-semibold text-white/72">{formatCurrency(item.amount, item.currency)}</p>
              </div>
            ))}
            {!recurring.length && <p className="text-sm text-white/38">No recurring payments detected yet.</p>}
          </div>
        </Card>
      </section>
    </div>
  );
}
