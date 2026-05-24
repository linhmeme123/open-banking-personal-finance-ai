"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { getStoredSession } from "@/lib/session";

type Transaction = {
  id: number;
  transaction_time: string;
  description: string;
  merchant_name: string | null;
  amount: number;
  currency: string;
  direction: string;
  category: string | null;
  category_confidence: number | null;
};

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [category, setCategory] = useState("");
  const [month, setMonth] = useState("2026-05");

  async function load() {
    const session = getStoredSession();
    if (!session) return;
    const params = new URLSearchParams();
    if (month) params.set("month", month);
    if (category) params.set("category", category);
    const query = params.toString() ? `?${params.toString()}` : "";
    setTransactions(await apiGet<Transaction[]>(`/api/transactions${query}`, session.access_token));
  }

  useEffect(() => {
    load().catch(() => setTransactions([]));
  }, []);

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">Transactions</h1>
        <p className="mt-2 text-slate-600">Synced transactions with AI categories and filters.</p>
      </div>

      <section className="flex flex-wrap gap-3 rounded-lg border bg-white p-4 shadow-sm">
        <input className="rounded-lg border px-3 py-2" value={month} onChange={(event) => setMonth(event.target.value)} />
        <select className="rounded-lg border px-3 py-2" value={category} onChange={(event) => setCategory(event.target.value)}>
          <option value="">All categories</option>
          <option value="food_drink">food_drink</option>
          <option value="transport">transport</option>
          <option value="shopping">shopping</option>
          <option value="subscription">subscription</option>
          <option value="income">income</option>
        </select>
        <button className="rounded-lg bg-slate-900 px-4 py-2 text-white" onClick={() => load()}>
          Apply
        </button>
      </section>

      <div className="overflow-hidden rounded-lg border bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="p-4">Time</th>
              <th className="p-4">Description</th>
              <th className="p-4">Category</th>
              <th className="p-4 text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx) => (
              <tr key={tx.id} className="border-t">
                <td className="p-4">{new Date(tx.transaction_time).toLocaleDateString("vi-VN")}</td>
                <td className="p-4">
                  <div className="font-medium">{tx.description}</div>
                  <div className="text-xs text-slate-500">{tx.merchant_name}</div>
                </td>
                <td className="p-4">
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs">{tx.category ?? "uncategorized"}</span>
                </td>
                <td className="p-4 text-right font-semibold">
                  {tx.amount.toLocaleString()} {tx.currency}
                </td>
              </tr>
            ))}
            {transactions.length === 0 && (
              <tr>
                <td className="p-4 text-slate-600" colSpan={4}>
                  No transactions found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
