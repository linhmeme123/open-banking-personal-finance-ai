"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import { getStoredSession } from "@/lib/session";

type Budget = {
  id: number;
  category: string;
  month: string;
  monthly_limit: number;
};

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [category, setCategory] = useState("food_drink");
  const [month, setMonth] = useState("2026-05");
  const [monthlyLimit, setMonthlyLimit] = useState("1000000");

  async function load() {
    const session = getStoredSession();
    if (!session) return;
    setBudgets(await apiGet<Budget[]>("/api/budgets", session.access_token));
  }

  async function save() {
    const session = getStoredSession();
    if (!session) return;
    await apiPost<Budget>(
      "/api/budgets",
      { category, month, monthly_limit: Number(monthlyLimit) },
      session.access_token,
    );
    await load();
  }

  useEffect(() => {
    load().catch(() => setBudgets([]));
  }, []);

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">Budgets</h1>
        <p className="mt-2 text-slate-600">Monthly category limits used by dashboard and AI coach.</p>
      </div>

      <section className="grid gap-3 rounded-lg border bg-white p-5 shadow-sm md:grid-cols-[1fr_1fr_1fr_auto]">
        <select className="rounded-lg border px-3 py-2" value={category} onChange={(event) => setCategory(event.target.value)}>
          <option value="food_drink">food_drink</option>
          <option value="transport">transport</option>
          <option value="shopping">shopping</option>
          <option value="subscription">subscription</option>
        </select>
        <input className="rounded-lg border px-3 py-2" value={month} onChange={(event) => setMonth(event.target.value)} />
        <input
          className="rounded-lg border px-3 py-2"
          inputMode="numeric"
          value={monthlyLimit}
          onChange={(event) => setMonthlyLimit(event.target.value)}
        />
        <button className="rounded-lg bg-slate-900 px-4 py-2 text-white" onClick={save}>
          Save
        </button>
      </section>

      <section className="grid gap-3">
        {budgets.map((budget) => (
          <div key={budget.id} className="flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-white p-4 shadow-sm">
            <div>
              <p className="font-semibold">{budget.category}</p>
              <p className="text-sm text-slate-600">{budget.month}</p>
            </div>
            <p className="font-semibold">{budget.monthly_limit.toLocaleString()} VND</p>
          </div>
        ))}
      </section>
    </div>
  );
}
