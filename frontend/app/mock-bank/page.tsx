"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, Landmark, Plus, Radio, RefreshCw, Send } from "lucide-react";
import { Brand } from "@/components/Brand";
import { getApiErrorMessage } from "@/lib/api";
import { formatCurrency } from "@/lib/format";
import {
  BankProvider,
  createMockBankAccount,
  createMockBankTransaction,
  generateMockBankTransaction,
  getMockBankAccounts,
  getMockBankProviders,
  getMockBankTransactions,
  MockBankAccount,
  MockBankTransaction,
  sendMockBankWebhook,
} from "@/lib/finance";

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
  const [message, setMessage] = useState("");

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
      });
      setMessage("Transaction added to the mock provider. Sync it or send a webhook.");
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
    try {
      const result = await sendMockBankWebhook(providerCode, transactionId);
      setMessage(`Webhook accepted. ${result.transactions_added} transaction imported into the finance app.`);
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

        <section className="glass-panel flex flex-wrap gap-3 p-4">
          <input className="form-control min-w-60 flex-1" onChange={(event) => setAccountName(event.target.value)} placeholder="New account name" value={accountName} />
          <button className="button-secondary" disabled={!providerCode || !accountName.trim()} onClick={createAccount} type="button">
            <Plus className="h-4 w-4" aria-hidden="true" />
            Create account
          </button>
        </section>

        <section className="glass-panel grid gap-3 p-4 md:grid-cols-5">
          <input className="form-control" onChange={(event) => setDescription(event.target.value)} placeholder="Description" value={description} />
          <input className="form-control" onChange={(event) => setMerchant(event.target.value)} placeholder="Merchant" value={merchant} />
          <input className="form-control" min="0" onChange={(event) => setAmount(event.target.value)} placeholder="Amount" type="number" value={amount} />
          <select className="form-control" onChange={(event) => setDirection(event.target.value)} value={direction}>
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
          <button className="button-primary" disabled={!accountId} onClick={createTransaction} type="button">
            <Plus className="h-4 w-4" aria-hidden="true" />
            Add
          </button>
        </section>

        <div className="flex flex-wrap gap-2">
          <button className="button-secondary" disabled={!accountId} onClick={generate} type="button">
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Generate random
          </button>
          <Link className="button-secondary" href="/app/open-banking">
            <Landmark className="h-4 w-4" aria-hidden="true" />
            Open Banking
          </Link>
        </div>

        <section className="glass-panel overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-white/[0.08] bg-white/[0.025] text-[10px] uppercase text-white/35">
              <tr><th className="px-5 py-4">Date</th><th className="px-5 py-4">Activity</th><th className="px-5 py-4">Amount</th><th className="px-5 py-4 text-right">Webhook</th></tr>
            </thead>
            <tbody>
              {transactions.map((item) => (
                <tr className="border-b border-white/[0.06] last:border-0" key={item.external_transaction_id}>
                  <td className="px-5 py-4 text-white/42">{new Date(item.transaction_time).toLocaleString("vi-VN")}</td>
                  <td className="px-5 py-4"><p className="text-white">{item.merchant_name || item.description}</p><p className="mt-1 text-xs text-white/32">{item.description}</p></td>
                  <td className={`px-5 py-4 font-semibold ${item.direction === "income" ? "text-emerald-300" : "text-white"}`}>{formatCurrency(item.amount)}</td>
                  <td className="px-5 py-4 text-right">
                    <button aria-label="Send webhook" className="inline-flex rounded-md p-2 text-pink-200 hover:bg-pink-300/10" onClick={() => sendWebhook(item.external_transaction_id)} title="Send webhook" type="button">
                      <Send className="h-4 w-4" aria-hidden="true" />
                    </button>
                  </td>
                </tr>
              ))}
              {!transactions.length && <tr><td className="px-5 py-8 text-white/42" colSpan={4}><Radio className="mr-2 inline h-4 w-4" aria-hidden="true" />No mock activity yet.</td></tr>}
            </tbody>
          </table>
        </section>
      </div>
    </main>
  );
}
