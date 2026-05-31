"use client";

import { useEffect, useState } from "react";
import { BankProviderCard } from "@/components/BankProviderCard";
import { PageHeader } from "@/components/PageHeader";
import { getApiErrorMessage } from "@/lib/api";
import {
  BankConnection,
  BankProvider,
  connectProvider,
  getConnections,
  getProviders,
  ProviderType,
  syncProvider,
} from "@/lib/finance";

const PROVIDER_GROUPS: { type: ProviderType; title: string; description: string }[] = [
  { type: "digital_bank", title: "Digital banks", description: "App-first banking accounts for everyday cashflow." },
  { type: "fintech", title: "Fintech wallets", description: "Bring wallet activity into your consolidated view." },
  { type: "traditional_bank", title: "Traditional banks", description: "Connect core banking accounts through the sandbox layer." },
];

export default function OpenBankingPage() {
  const [providers, setProviders] = useState<BankProvider[]>([]);
  const [connections, setConnections] = useState<BankConnection[]>([]);
  const [activeProvider, setActiveProvider] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    const [nextProviders, nextConnections] = await Promise.all([getProviders(), getConnections()]);
    setProviders(nextProviders);
    setConnections(nextConnections);
  }

  useEffect(() => {
    load().catch((error) => setMessage(getApiErrorMessage(error, "Unable to load providers.")));
  }, []);

  async function connect(providerCode: string) {
    setActiveProvider(providerCode);
    setMessage("");
    try {
      const connection = await connectProvider(providerCode);
      setMessage(`${connection.provider_name} is connected. Sync to import account activity.`);
      setConnections(await getConnections());
    } catch (error) {
      setMessage(getApiErrorMessage(error, "Unable to connect this provider."));
    } finally {
      setActiveProvider("");
    }
  }

  async function sync(providerCode: string) {
    setActiveProvider(providerCode);
    setMessage("");
    try {
      const result = await syncProvider(providerCode);
      setMessage(`Sync complete. ${result.created_accounts} accounts and ${result.created_transactions} transactions imported.`);
      setConnections(await getConnections());
    } catch (error) {
      setMessage(getApiErrorMessage(error, "Unable to sync this provider."));
    } finally {
      setActiveProvider("");
    }
  }

  return (
    <div className="grid gap-7">
      <PageHeader
        description="Grant scoped sandbox consent, then sync balances and transaction activity into your finance workspace."
        eyebrow="Secure connections"
        title="Connect your banks"
      />

      {message && <p className="rounded-lg border border-pink-300/15 bg-pink-300/[0.05] px-4 py-3 text-sm text-pink-100">{message}</p>}

      {PROVIDER_GROUPS.map((group) => {
        const groupedProviders = providers.filter((provider) => provider.type === group.type);
        return (
          <section className="grid gap-4" key={group.type}>
            <div>
              <h2 className="text-base font-semibold text-white">{group.title}</h2>
              <p className="mt-1 text-sm text-white/38">{group.description}</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {groupedProviders.map((provider) => (
                <BankProviderCard
                  connection={connections.find((connection) => connection.provider_code === provider.code)}
                  key={provider.code}
                  loading={activeProvider === provider.code}
                  onConnect={() => connect(provider.code)}
                  onSync={() => sync(provider.code)}
                  provider={provider}
                />
              ))}
            </div>
          </section>
        );
      })}

      <section className="glass-subtle px-4 py-3 text-xs leading-6 text-white/38">
        Connected providers use scoped Open Banking sandbox APIs. {connections.length} provider{connections.length === 1 ? " is" : "s are"} connected to this profile.
      </section>
    </div>
  );
}
