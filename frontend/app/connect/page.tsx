"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import { DemoSession, demoLogin, getStoredSession } from "@/lib/session";

type Provider = { code: string; name: string };
type Connection = {
  provider_code: string;
  provider_name: string;
  status: string;
  consent_scope: string;
  last_synced_at: string | null;
};

export default function ConnectPage() {
  const [session, setSession] = useState<DemoSession | null>(null);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState("BANK_A");
  const [connection, setConnection] = useState<Connection | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stored = getStoredSession();
    setSession(stored);
    apiGet<Provider[]>("/api/open-banking/providers", stored?.access_token)
      .then(setProviders)
      .catch(() => setProviders([]));
  }, []);

  async function ensureSession() {
    if (session) return session;
    const nextSession = await demoLogin();
    setSession(nextSession);
    return nextSession;
  }

  async function connect() {
    setLoading(true);
    setMessage("");
    try {
      const activeSession = await ensureSession();
      const nextConnection = await apiPost<Connection>(
        "/api/open-banking/connect",
        { provider_code: selectedProvider, scope: "accounts:read transactions:read" },
        activeSession.access_token,
      );
      setConnection(nextConnection);
      setMessage(`${nextConnection.provider_name} connected`);
    } finally {
      setLoading(false);
    }
  }

  async function sync() {
    setLoading(true);
    setMessage("");
    try {
      const activeSession = await ensureSession();
      const result = await apiPost<{ status: string; created_transactions: number }>(
        "/api/open-banking/sync",
        { provider_code: selectedProvider },
        activeSession.access_token,
      );
      setMessage(`Sync complete: ${result.created_transactions} new transactions`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">Connect bank</h1>
        <p className="mt-2 text-slate-600">Grant sandbox consent and sync your personal finance data.</p>
      </div>

      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <label className="text-sm font-semibold text-slate-600" htmlFor="provider">
          Provider
        </label>
        <select
          id="provider"
          className="mt-2 w-full rounded-lg border p-3"
          value={selectedProvider}
          onChange={(event) => setSelectedProvider(event.target.value)}
        >
          {providers.map((provider) => (
            <option key={provider.code} value={provider.code}>
              {provider.name}
            </option>
          ))}
        </select>

        <div className="mt-5 flex flex-wrap gap-3">
          <button className="rounded-lg bg-slate-900 px-4 py-2 text-white disabled:opacity-60" disabled={loading} onClick={connect}>
            Grant consent
          </button>
          <button className="rounded-lg border px-4 py-2 disabled:opacity-60" disabled={loading} onClick={sync}>
            Sync data
          </button>
        </div>

        {connection && (
          <div className="mt-5 rounded-lg bg-slate-50 p-4 text-sm">
            <p className="font-semibold">{connection.provider_name}</p>
            <p className="text-slate-600">Scope: {connection.consent_scope}</p>
          </div>
        )}
        {message && <p className="mt-4 text-sm font-medium text-slate-700">{message}</p>}
      </section>
    </div>
  );
}
