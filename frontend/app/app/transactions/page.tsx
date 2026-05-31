"use client";

import { useEffect, useState } from "react";
import { BrainCircuit, Landmark, Loader2, ReceiptText, WandSparkles } from "lucide-react";
import { EmptyState } from "@/components/EmptyState";
import { PageHeader } from "@/components/PageHeader";
import { TransactionFilters } from "@/components/TransactionFilters";
import { TransactionTable } from "@/components/TransactionTable";
import { getApiErrorMessage } from "@/lib/api";
import {
  BankConnection,
  categorizeTransaction,
  categorizeUncategorized,
  EMPTY_TRANSACTION_FILTERS,
  FinanceTransaction,
  getConnections,
  getTransactions,
  TransactionFilterValues,
} from "@/lib/finance";

export default function TransactionsPage() {
  const [connections, setConnections] = useState<BankConnection[]>([]);
  const [transactions, setTransactions] = useState<FinanceTransaction[]>([]);
  const [filters, setFilters] = useState<TransactionFilterValues>(EMPTY_TRANSACTION_FILTERS);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function load(activeFilters = filters) {
    setBusy(true);
    setMessage("");
    try {
      const [nextConnections, nextTransactions] = await Promise.all([getConnections(), getTransactions(activeFilters)]);
      setConnections(nextConnections);
      setTransactions(nextTransactions);
      setSelectedId((current) => nextTransactions.some((transaction) => transaction.id === current) ? current : null);
    } catch (error) {
      setMessage(getApiErrorMessage(error, "Unable to load transactions."));
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    load(EMPTY_TRANSACTION_FILTERS);
  }, []);

  async function categorizeSelected() {
    if (!selectedId) return;
    setBusy(true);
    setMessage("");
    try {
      const result = await categorizeTransaction(selectedId);
      setMessage(`Transaction categorized as ${result.category}.`);
      await load();
    } catch (error) {
      setMessage(getApiErrorMessage(error, "Unable to categorize this transaction."));
      setBusy(false);
    }
  }

  async function categorizeAll() {
    setBusy(true);
    setMessage("");
    try {
      const result = await categorizeUncategorized(filters.provider_code);
      setMessage(`${result.categorized_count} uncategorized transactions processed.`);
      await load();
    } catch (error) {
      setMessage(getApiErrorMessage(error, "Unable to categorize transactions."));
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-6">
      <PageHeader
        action={
          <div className="flex flex-wrap gap-2">
            <button className="button-secondary" disabled={!selectedId || busy} onClick={categorizeSelected} type="button">
              {busy && selectedId ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <BrainCircuit className="h-4 w-4" aria-hidden="true" />}
              Categorize selected
            </button>
            <button className="button-secondary" disabled={busy} onClick={categorizeAll} type="button">
              <WandSparkles className="h-4 w-4" aria-hidden="true" />
              Categorize uncategorized
            </button>
          </div>
        }
        description="Filter synced activity across providers and review AI-assisted transaction categories."
        eyebrow="Cashflow ledger"
        title="Transactions"
      />

      {message && <p className="rounded-lg border border-pink-300/15 bg-pink-300/[0.05] px-4 py-3 text-sm text-pink-100">{message}</p>}

      <TransactionFilters busy={busy} connections={connections} onApply={() => load()} onChange={setFilters} values={filters} />

      {transactions.length > 0 && <TransactionTable onSelect={setSelectedId} selectedId={selectedId} transactions={transactions} />}

      {!busy && transactions.length === 0 && (
        <EmptyState
          action={connections.length === 0 ? { href: "/app/open-banking", label: "Connect a banking provider" } : undefined}
          description={connections.length === 0 ? "Connect and sync a provider before reviewing transaction activity." : "No synced activity matches the current filter set."}
          icon={connections.length === 0 ? Landmark : ReceiptText}
          title={connections.length === 0 ? "No transaction sources yet" : "No matching transactions"}
        />
      )}
    </div>
  );
}
