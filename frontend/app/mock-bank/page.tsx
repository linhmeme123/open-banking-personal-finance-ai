"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, CheckCircle2, Clock3, ExternalLink, Landmark, ListTree, Loader2, Plus, Radio, RefreshCw, Send, WalletCards, X } from "lucide-react";
import { Brand } from "@/components/Brand";
import { ApiError, getApiErrorMessage } from "@/lib/api";
import { formatCurrency } from "@/lib/format";
import {
  BankProvider,
  MockBankEvent,
  TRANSACTION_CATEGORIES,
  createMockBankAccount,
  createMockBankTransaction,
  generateMockBankTransaction,
  getMockBankAccounts,
  getMockBankProviders,
  getMockBankTransactionEvents,
  getMockBankTransactions,
  MockBankAccount,
  MockBankTransaction,
  sendMockBankWebhook,
  syncProvider,
} from "@/lib/finance";

function StatusBadge({ value }: { value: string }) {
  const tone = value === "synced" || value === "delivered"
    ? "border-emerald-300/20 bg-emerald-300/10 text-emerald-200"
    : value === "failed"
      ? "border-red-300/20 bg-red-300/10 text-red-200"
      : "border-amber-300/20 bg-amber-300/10 text-amber-100";
  return <span className={`inline-flex rounded-full border px-2 py-1 text-[10px] font-semibold uppercase tracking-wide ${tone}`}>{value}</span>;
}

export default function MockBankPage() {
  const [providers, setProviders] = useState<BankProvider[]>([]);
  const [providerCode, setProviderCode] = useState("");
  const [accounts, setAccounts] = useState<MockBankAccount[]>([]);
  const [accountId, setAccountId] = useState("");
  const [transactions, setTransactions] = useState<MockBankTransaction[]>([]);
  const [accountName, setAccountName] = useState("New checking account");
  const [description, setDescription] = useState("Highlands Coffee");
  const [merchant, setMerchant] = useState("Highlands Coffee");
  const [amount, setAmount] = useState("65000");
  const [direction, setDirection] = useState("expense");
  const [category, setCategory] = useState("");
  const [transactionTime, setTransactionTime] = useState("");
  const [timeline, setTimeline] = useState<MockBankEvent[]>([]);
  const [timelineTransaction, setTimelineTransaction] = useState<MockBankTransaction | null>(null);
  const [message, setMessage] = useState("");
  const [pushingTransactionId, setPushingTransactionId] = useState<string | null>(null);
  const [recentlyPushedTransactionId, setRecentlyPushedTransactionId] = useState<string | null>(null);
  const [pushErrors, setPushErrors] = useState<Record<string, string>>({});
  const selectedAccount = accounts.find((account) => account.external_account_id === accountId);
  const selectedProvider = providers.find((provider) => provider.code === providerCode);

  async function load(nextProvider = providerCode, nextAccount = accountId) {
    if (!nextProvider) return;
    const nextAccounts = await getMockBankAccounts(nextProvider);
    const resolvedAccount = nextAccount || nextAccounts[0]?.external_account_id || "";
    setAccounts(nextAccounts);
    setAccountId(resolvedAccount);
    setTransactions(await getMockBankTransactions(nextProvider, resolvedAccount));
  }

  useEffect(() => {
    getMockBankProviders()
      .then((items) => {
        setProviders(items);
        setProviderCode(items[0]?.code || "");
        return load(items[0]?.code || "", "");
      })
      .catch((error) => setMessage(getApiErrorMessage(error)));
  }, []);

  async function createTransaction() {
    try {
      await createMockBankTransaction({
        provider_code: providerCode,
        external_account_id: accountId,
        description,
        merchant_name: merchant,
        amount: direction === "expense" ? -Math.abs(Number(amount)) : Math.abs(Number(amount)),
        direction,
        category: category || undefined,
        transaction_time: transactionTime || undefined,
      });
      setMessage("Transaction added to the mock provider. Sync it or push it to Velora.");
      await load();
    } catch (error) {
      setMessage(getApiErrorMessage(error));
    }
  }

  async function createAccount() {
    try {
      const account = await createMockBankAccount(providerCode, accountName);
      setMessage("Mock bank account created.");
      await load(providerCode, account.external_account_id);
    } catch (error) {
      setMessage(getApiErrorMessage(error));
    }
  }

  async function generate() {
    try {
      await generateMockBankTransaction(providerCode, accountId);
      setMessage("Random transaction generated.");
      await load();
    } catch (error) {
      setMessage(getApiErrorMessage(error));
    }
  }

  async function sendWebhook(transactionId: string) {
    setPushingTransactionId(transactionId);
    setPushErrors((current) => ({ ...current, [transactionId]: "" }));
    try {
      const transaction = transactions.find((item) => item.external_transaction_id === transactionId);
      console.log("[mock-bank] sending webhook", transaction);
      const result = await sendMockBankWebhook(providerCode, transactionId);
      console.log("[mock-bank] webhook response", result);
      setRecentlyPushedTransactionId(transactionId);
      window.setTimeout(() => setRecentlyPushedTransactionId(null), 1800);
      setMessage(result.status === "already_synced"
        ? "This transaction was already sent to Velora."
        : "Bank event delivered. The transaction is now available in Velora Transactions.");
      await load();
      await openTimeline(transactionId);
    } catch (error) {
      const detail = error instanceof ApiError && (error.status === 401 || error.status === 403)
        ? "Sign in to Velora first, then connect this mock provider in Open Banking."
        : getApiErrorMessage(error);
      setPushErrors((current) => ({ ...current, [transactionId]: detail }));
      setMessage(`Unable to push bank event: ${detail}`);
      try {
        await load();
      } catch {
        // Keep the original push error visible when refresh also fails.
      }
    } finally {
      setPushingTransactionId(null);
    }
  }

  async function syncToOpenBanking() {
    try {
      const result = await syncProvider(providerCode);
      setMessage(`Open Banking sync complete. ${result.created_transactions} new transactions imported.`);
      await load();
    } catch (error) {
      setMessage(getApiErrorMessage(error));
    }
  }

  async function openTimeline(transactionId: string) {
    try {
      const transaction = transactions.find((item) => item.external_transaction_id === transactionId) || null;
      setTimelineTransaction(transaction);
      setTimeline(await getMockBankTransactionEvents(providerCode, transactionId));
    } catch (error) {
      setMessage(getApiErrorMessage(error));
    }
  }

  return (
    <main className="min-h-screen bg-[#08070b]">
      <header className="border-b border-white/[0.08] bg-[#0b090e]/90">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8">
          <Brand />
          <Link className="button-secondary" href="/">
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
            Velora app
          </Link>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-5 py-8 sm:px-8">
        <div>
          <p className="eyebrow">Developer console</p>
          <h1 className="mt-2 text-3xl font-semibold text-white">Mock Bank Console</h1>
          <p className="mt-2 text-sm text-white/42">Create source-bank activity and push it through the same adapter contract used by Open Banking sync.</p>
        </div>

        {message && <p className="rounded-lg border border-pink-300/15 bg-pink-300/[0.05] px-4 py-3 text-sm text-pink-100">{message}</p>}

        <section className="glass-panel grid gap-3 p-4 md:grid-cols-2">
          <select className="form-control" onChange={(event) => { setProviderCode(event.target.value); load(event.target.value, ""); }} value={providerCode}>
            {providers.map((provider) => <option key={provider.code} value={provider.code}>{provider.name}</option>)}
          </select>
          <select className="form-control" onChange={(event) => { setAccountId(event.target.value); load(providerCode, event.target.value); }} value={accountId}>
            {accounts.map((account) => <option key={account.external_account_id} value={account.external_account_id}>{account.account_name} - {formatCurrency(account.balance)}</option>)}
          </select>
        </section>

        {selectedAccount && (
          <section className="glass-panel grid gap-4 p-5 sm:grid-cols-[1fr_auto]">
            <div>
              <p className="eyebrow">Current balance</p>
              <p className="mt-2 text-3xl font-semibold text-white">{formatCurrency(selectedAccount.balance)}</p>
              <p className="mt-3 text-sm text-white/42">{selectedAccount.account_type} · {selectedProvider?.name}</p>
            </div>
            <div className="flex items-center gap-3 text-sm text-white/42">
              <WalletCards className="h-5 w-5 text-pink-200" aria-hidden="true" />
              <span>Updated<br />{new Date(selectedAccount.last_updated_at).toLocaleString("vi-VN")}</span>
            </div>
          </section>
        )}

        <section className="glass-panel flex flex-wrap gap-3 p-4">
          <input className="form-control min-w-60 flex-1" onChange={(event) => setAccountName(event.target.value)} placeholder="New account name" value={accountName} />
          <button className="button-secondary" disabled={!providerCode || !accountName.trim()} onClick={createAccount} type="button">
            <Plus className="h-4 w-4" aria-hidden="true" />
            Create account
          </button>
        </section>

        <section className="glass-panel grid gap-3 p-4 md:grid-cols-3">
          <input className="form-control" onChange={(event) => setDescription(event.target.value)} placeholder="Description" value={description} />
          <input className="form-control" onChange={(event) => setMerchant(event.target.value)} placeholder="Merchant" value={merchant} />
          <input className="form-control" min="0" onChange={(event) => setAmount(event.target.value)} placeholder="Amount" type="number" value={amount} />
          <select className="form-control" onChange={(event) => setDirection(event.target.value)} value={direction}>
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
          <select className="form-control" onChange={(event) => setCategory(event.target.value)} value={category}>
            <option value="">Auto category</option>
            {TRANSACTION_CATEGORIES.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
          <input className="form-control" onChange={(event) => setTransactionTime(event.target.value)} type="datetime-local" value={transactionTime} />
          <button className="button-primary" disabled={!accountId} onClick={createTransaction} type="button">
            <Plus className="h-4 w-4" aria-hidden="true" />
            Add Transaction
          </button>
        </section>

        <div className="flex flex-wrap gap-2">
          <button className="button-secondary" disabled={!accountId} onClick={generate} type="button">
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Generate random
          </button>
          <button className="button-secondary" disabled={!accountId} onClick={syncToOpenBanking} type="button">
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Sync to Open Banking
          </button>
          <Link className="button-secondary" href="/app/transactions">
            <Landmark className="h-4 w-4" aria-hidden="true" />
            Open Velora Transactions
          </Link>
        </div>

        <section className="glass-panel overflow-x-auto">
          <table className="w-full min-w-[1120px] text-left text-sm">
            <thead className="border-b border-white/[0.08] bg-white/[0.025] text-[10px] uppercase text-white/35">
              <tr><th className="px-5 py-4">Date</th><th className="px-5 py-4">Activity</th><th className="px-5 py-4">Amount</th><th className="px-5 py-4">Balance after</th><th className="px-5 py-4">Category</th><th className="px-5 py-4">Webhook</th><th className="px-5 py-4">Sync</th><th className="px-5 py-4 text-right">Actions</th></tr>
            </thead>
            <tbody>
              {transactions.map((item) => (
                <tr className="border-b border-white/[0.06] last:border-0" key={item.external_transaction_id}>
                  <td className="px-5 py-4 text-white/42">{new Date(item.transaction_time).toLocaleString("vi-VN")}</td>
                  <td className="px-5 py-4"><p className="text-white">{item.merchant_name || item.description}</p><p className="mt-1 text-xs text-white/32">{item.description}</p></td>
                  <td className={`px-5 py-4 font-semibold ${item.direction === "income" ? "text-emerald-300" : "text-white"}`}>{formatCurrency(item.amount)}</td>
                  <td className="px-5 py-4 text-white/62">{formatCurrency(item.balance_after)}</td>
                  <td className="px-5 py-4 text-white/62">{item.category || "Auto on sync"}</td>
                  <td className="px-5 py-4"><StatusBadge value={item.webhook_status} /></td>
                  <td className="px-5 py-4"><StatusBadge value={item.sync_status} /></td>
                  <td className="px-5 py-4 text-right">
                    <div className="flex justify-end">
                      <button className="button-secondary mr-2 px-3 py-2 text-xs" onClick={() => openTimeline(item.external_transaction_id)} type="button">
                        <ListTree className="h-4 w-4" aria-hidden="true" />
                        Timeline
                      </button>
                      <button
                        className={`button-secondary px-3 py-2 text-xs transition-all ${item.sync_status === "synced" ? "border-emerald-300/30 bg-emerald-300/10 text-emerald-200" : ""} ${recentlyPushedTransactionId === item.external_transaction_id ? "scale-105 shadow-lg shadow-emerald-500/20" : ""}`}
                        disabled={pushingTransactionId === item.external_transaction_id || item.sync_status === "synced"}
                        onClick={() => sendWebhook(item.external_transaction_id)}
                        type="button"
                      >
                        {pushingTransactionId === item.external_transaction_id
                          ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                          : item.sync_status === "synced"
                            ? <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
                            : <Send className="h-4 w-4" aria-hidden="true" />}
                        {pushingTransactionId === item.external_transaction_id
                          ? "Sending..."
                          : item.sync_status === "synced"
                            ? "Sent to Velora"
                            : "Push to Velora"}
                      </button>
                      {item.sync_status === "synced" && (
                        <Link
                          className="button-secondary ml-2 px-3 py-2 text-xs"
                          href={`/app/transactions?external_transaction_id=${encodeURIComponent(item.external_transaction_id)}`}
                        >
                          <ExternalLink className="h-4 w-4" aria-hidden="true" />
                          View in Velora
                        </Link>
                      )}
                    </div>
                    {pushErrors[item.external_transaction_id] && (
                      <div className="mt-2 flex items-center justify-end gap-2 text-xs text-red-200">
                        <span>{pushErrors[item.external_transaction_id]}</span>
                        <Link className="font-semibold text-pink-200 underline underline-offset-2" href="/app/open-banking">
                          Connect provider
                        </Link>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
              {!transactions.length && <tr><td className="px-5 py-8 text-white/42" colSpan={8}><Radio className="mr-2 inline h-4 w-4" aria-hidden="true" />No mock activity yet.</td></tr>}
            </tbody>
          </table>
        </section>
      </div>

      {timelineTransaction && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60">
          <aside className="h-full w-full max-w-md overflow-y-auto border-l border-white/[0.08] bg-[#100c14] p-6 shadow-2xl">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="eyebrow">Transaction timeline</p>
                <h2 className="mt-2 text-xl font-semibold text-white">{timelineTransaction.merchant_name || timelineTransaction.description}</h2>
              </div>
              <button className="rounded-md p-2 text-white/50 hover:bg-white/[0.06]" onClick={() => setTimelineTransaction(null)} type="button"><X className="h-4 w-4" aria-hidden="true" /></button>
            </div>
            <div className="mt-7 grid gap-4">
              {timeline.map((event) => (
                <div className="border-l border-pink-300/30 pl-4" key={`${event.event_type}-${event.created_at}`}>
                  <div className="flex items-center gap-2 text-xs text-white/35"><Clock3 className="h-3 w-3" aria-hidden="true" />{new Date(event.created_at).toLocaleString("vi-VN")}</div>
                  <p className="mt-1 text-sm text-white/78">{event.message}</p>
                </div>
              ))}
            </div>
          </aside>
        </div>
      )}
    </main>
  );
}
