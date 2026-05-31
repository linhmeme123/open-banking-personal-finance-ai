"use client";

import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { apiGet, apiPost } from "@/lib/api";
import { formatCategory, formatCurrency, getCurrentMonth } from "@/lib/format";
import { TRANSACTION_CATEGORIES } from "@/lib/finance";

type Budget = {
  id: number;
  category: string;
  month: string;
  monthly_limit: number;
};

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [category, setCategory] = useState("food");
  const [month, setMonth] = useState(getCurrentMonth());
  const [monthlyLimit, setMonthlyLimit] = useState("1000000");

  async function load() {
    setBudgets(await apiGet<Budget[]>("/api/budgets"));
  }

  async function save() {
    await apiPost<Budget>("/api/budgets", {
      category,
      month,
      monthly_limit: Number(monthlyLimit),
    });
    await load();
  }

  useEffect(() => {
    load().catch(() => setBudgets([]));
  }, []);

  return (
    <div className="grid gap-6">
      <PageHeader
        description="Set monthly limits by category. These targets also inform your dashboard and AI coach."
        eyebrow="Spending targets"
        title="Budgets"
      />

      <section className="glass-panel grid gap-3 p-4 md:grid-cols-[1fr_1fr_1fr_auto]">
        <select className="form-control" onChange={(event) => setCategory(event.target.value)} value={category}>
          {TRANSACTION_CATEGORIES.filter((item) => !["salary", "transfer", "unknown"].includes(item)).map((item) => (
            <option key={item} value={item}>{formatCategory(item)}</option>
          ))}
        </select>
        <input className="form-control" onChange={(event) => setMonth(event.target.value)} type="month" value={month} />
        <input className="form-control" inputMode="numeric" onChange={(event) => setMonthlyLimit(event.target.value)} value={monthlyLimit} />
        <button className="button-primary" onClick={save} type="button">
          <Save className="h-4 w-4" aria-hidden="true" />
          Save budget
        </button>
      </section>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {budgets.map((budget) => (
          <article className="glass-panel p-5" key={budget.id}>
            <p className="eyebrow">{budget.month}</p>
            <h2 className="mt-3 text-base font-semibold text-white">{formatCategory(budget.category)}</h2>
            <p className="mt-5 text-xl font-semibold text-white">{formatCurrency(budget.monthly_limit)}</p>
          </article>
        ))}
      </section>

      {!budgets.length && <p className="text-sm text-white/38">No monthly budgets saved yet.</p>}
    </div>
  );
}
