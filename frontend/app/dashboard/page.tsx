import { Card } from "@/components/Card";
import { apiGet, apiPost } from "@/lib/api";

type Summary = {
  income: number;
  expense: number;
  net_cashflow: number;
  category_breakdown: { category: string; amount: number }[];
};

async function getSummary() {
  try {
    return await apiGet<Summary>("/api/insights/monthly-summary");
  } catch {
    return null;
  }
}

export default async function DashboardPage() {
  const summary = await getSummary();

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="mt-2 text-slate-600">
          Tổng quan dòng tiền cá nhân từ dữ liệu ngân hàng giả lập.
        </p>
      </div>

      {!summary ? (
        <div className="rounded-2xl border bg-white p-6">
          <p className="text-slate-600">
            Chưa có dữ liệu. Hãy gọi API <code>POST /api/open-banking/sync</code> hoặc dùng Swagger tại backend.
          </p>
        </div>
      ) : (
        <>
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

          <Card title="Category Breakdown">
            <div className="grid gap-3">
              {summary.category_breakdown.map((item) => (
                <div key={item.category} className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                  <span className="font-medium">{item.category}</span>
                  <span>{item.amount.toLocaleString()} VND</span>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
