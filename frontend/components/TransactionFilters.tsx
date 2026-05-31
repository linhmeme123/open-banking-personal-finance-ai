import { Filter, Search } from "lucide-react";
import { formatCategory } from "@/lib/format";
import { BankConnection, TRANSACTION_CATEGORIES, TransactionFilterValues } from "@/lib/finance";

export function TransactionFilters({
  connections,
  values,
  busy,
  onChange,
  onApply,
}: {
  connections: BankConnection[];
  values: TransactionFilterValues;
  busy: boolean;
  onChange: (values: TransactionFilterValues) => void;
  onApply: () => void;
}) {
  function update(key: keyof TransactionFilterValues, value: string) {
    onChange({ ...values, [key]: value });
  }

  return (
    <section className="glass-panel grid gap-3 p-4 lg:grid-cols-4">
      <label className="relative lg:col-span-2">
        <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-white/32" aria-hidden="true" />
        <input className="form-control pl-9" onChange={(event) => update("search", event.target.value)} placeholder="Search merchant or description" type="search" value={values.search} />
      </label>
      <select className="form-control" onChange={(event) => update("provider_code", event.target.value)} value={values.provider_code}>
        <option value="">All providers</option>
        {connections.map((connection) => <option key={connection.provider_code} value={connection.provider_code}>{connection.provider_name}</option>)}
      </select>
      <select className="form-control" onChange={(event) => update("category", event.target.value)} value={values.category}>
        <option value="">All categories</option>
        {TRANSACTION_CATEGORIES.map((category) => <option key={category} value={category}>{formatCategory(category)}</option>)}
      </select>
      <select className="form-control" onChange={(event) => update("direction", event.target.value)} value={values.direction}>
        <option value="">All directions</option>
        <option value="income">Income</option>
        <option value="expense">Expense</option>
      </select>
      <input className="form-control" onChange={(event) => update("date_from", event.target.value)} title="From date" type="date" value={values.date_from} />
      <input className="form-control" onChange={(event) => update("date_to", event.target.value)} title="To date" type="date" value={values.date_to} />
      <div className="grid grid-cols-2 gap-3">
        <input className="form-control" min="0" onChange={(event) => update("min_amount", event.target.value)} placeholder="Min amount" type="number" value={values.min_amount} />
        <input className="form-control" min="0" onChange={(event) => update("max_amount", event.target.value)} placeholder="Max amount" type="number" value={values.max_amount} />
      </div>
      <button className="button-primary lg:col-start-4" disabled={busy} onClick={onApply} type="button">
        <Filter className="h-4 w-4" aria-hidden="true" />
        Apply filters
      </button>
    </section>
  );
}
