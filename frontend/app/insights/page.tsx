"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/Card";
import { apiGet } from "@/lib/api";
import { getStoredSession } from "@/lib/session";

type Breakdown = { category: string; amount: number };
type Recurring = {
  merchant_name: string;
  amount: number;
  currency: string;
  occurrences: number;
  latest_transaction_time: string;
};

export default function InsightsPage() {
  const [breakdown, setBreakdown] = useState<Breakdown[]>([]);
  const [recurring, setRecurring] = useState<Recurring[]>([]);

  useEffect(() => {
    const session = getStoredSession();
    if (!session) return;
    Promise.all([
      apiGet<Breakdown[]>("/api/insights/category-breakdown", session.access_token),
      apiGet<Recurring[]>("/api/insights/recurring-payments", session.access_token),
    ])
      .then(([nextBreakdown, nextRecurring]) => {
        setBreakdown(nextBreakdown);
        setRecurring(nextRecurring);
      })
      .catch(() => {
        setBreakdown([]);
        setRecurring([]);
      });
  }, []);

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">Insights</h1>
        <p className="mt-2 text-slate-600">Category spending and recurring payment detection.</p>
      </div>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card title="Category Breakdown">
          <div className="grid gap-3">
            {breakdown.map((item) => (
              <div key={item.category} className="flex justify-between rounded-lg bg-slate-50 p-3">
                <span className="font-medium">{item.category}</span>
                <span>{item.amount.toLocaleString()} VND</span>
              </div>
            ))}
          </div>
        </Card>
        <Card title="Recurring Payments">
          <div className="grid gap-3">
            {recurring.map((item) => (
              <div key={`${item.merchant_name}-${item.amount}`} className="rounded-lg bg-slate-50 p-3">
                <p className="font-medium">{item.merchant_name}</p>
                <p className="text-sm text-slate-600">
                  {item.amount.toLocaleString()} {item.currency} over {item.occurrences} payments
                </p>
              </div>
            ))}
            {recurring.length === 0 && <p className="text-sm text-slate-600">No recurring payments detected.</p>}
          </div>
        </Card>
      </section>
    </div>
  );
}
