import { apiGet } from "@/lib/api";

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

async function getTransactions() {
  try {
    return await apiGet<Transaction[]>("/api/transactions");
  } catch {
    return [];
  }
}

export default async function TransactionsPage() {
  const transactions = await getTransactions();

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">Transactions</h1>
        <p className="mt-2 text-slate-600">
          Danh sách giao dịch đã được AI phân loại.
        </p>
      </div>

      <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
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
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs">
                    {tx.category ?? "uncategorized"}
                  </span>
                </td>
                <td className="p-4 text-right font-semibold">
                  {tx.amount.toLocaleString()} {tx.currency}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
