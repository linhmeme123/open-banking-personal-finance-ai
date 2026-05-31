import { formatCategory, formatCurrency } from "@/lib/format";
import { FinanceTransaction } from "@/lib/finance";

export function TransactionTable({
  transactions,
  selectedId,
  onSelect,
}: {
  transactions: FinanceTransaction[];
  selectedId: number | null;
  onSelect: (transactionId: number) => void;
}) {
  return (
    <section className="glass-panel overflow-x-auto">
      <table className="w-full min-w-[960px] text-left text-sm">
        <thead className="border-b border-white/[0.08] bg-white/[0.025] text-[10px] font-semibold uppercase text-white/35">
          <tr>
            <th className="w-10 px-5 py-4"><span className="sr-only">Select</span></th>
            <th className="px-3 py-4">Date</th>
            <th className="px-3 py-4">Merchant</th>
            <th className="px-3 py-4">Provider / account</th>
            <th className="px-3 py-4">Category</th>
            <th className="px-5 py-4 text-right">Amount</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr className="border-b border-white/[0.06] last:border-0" key={transaction.id}>
              <td className="px-5 py-4">
                <input aria-label={`Select ${transaction.description}`} checked={selectedId === transaction.id} className="accent-pink-500" name="selected-transaction" onChange={() => onSelect(transaction.id)} type="radio" />
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-white/42">{new Date(transaction.transaction_time).toLocaleDateString("vi-VN")}</td>
              <td className="px-3 py-4">
                <p className="font-medium text-white">{transaction.merchant_name || transaction.description}</p>
                <p className="mt-1 text-xs text-white/32">{transaction.description}</p>
              </td>
              <td className="px-3 py-4">
                <p className="text-white/68">{transaction.provider_name}</p>
                <p className="mt-1 text-xs text-white/32">{transaction.account_name}</p>
              </td>
              <td className="px-3 py-4">
                <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-xs text-white/55">
                  {formatCategory(transaction.category ?? "uncategorized")}
                </span>
                {transaction.category_confidence !== null && <p className="mt-2 text-[10px] text-white/30">{Math.round(transaction.category_confidence * 100)}% confidence</p>}
              </td>
              <td className={`whitespace-nowrap px-5 py-4 text-right font-semibold ${transaction.direction === "income" ? "text-emerald-300" : "text-white"}`}>
                {formatCurrency(transaction.amount, transaction.currency)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
