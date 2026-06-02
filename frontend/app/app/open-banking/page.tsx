"use client";

import { useEffect, useState } from "react";
import { Loader2, ShieldCheck, X } from "lucide-react";
import { BankProviderCard } from "@/components/BankProviderCard";
import { PageHeader } from "@/components/PageHeader";
import { getApiErrorMessage } from "@/lib/api";
import {
  BankConnection,
  BankProvider,
  ConnectionInitiation,
  authorizeProviderConnection,
  disconnectProvider,
  getConnections,
  getProviders,
  initiateProviderConnection,
  ProviderType,
  syncProvider,
} from "@/lib/finance";

const PROVIDER_GROUPS: { type: ProviderType; title: string; description: string }[] = [
  { type: "mock_bank", title: "Banks", description: "Use the local bank console to simulate realistic account activity." },
  { type: "sandbox", title: "Sandboxes", description: "Test providers with simulated authorization and consent. No real bank data is used." },
  { type: "real_partner", title: "Real partners", description: "Partner integrations can join through the same provider contract." },
];

function ConnectionModal({
  initiation,
  loading,
  onAuthorize,
  onClose,
}: {
  initiation: ConnectionInitiation;
  loading: boolean;
  onAuthorize: (values: {
    username: string;
    account_number: string;
    otp_code: string;
    scopes: string[];
    selected_account_ids: string[];
  }) => Promise<void>;
  onClose: () => void;
}) {
  const [username, setUsername] = useState("");
  const [accountNumber, setAccountNumber] = useState("");
  const [otpCode, setOtpCode] = useState("123456");
  const [scopes, setScopes] = useState(initiation.available_scopes);
  const [selectedAccountIds, setSelectedAccountIds] = useState(
    initiation.available_accounts.map((account) => account.external_account_id),
  );
  const [error, setError] = useState("");
  const isMockBank = initiation.provider.type === "mock_bank";

  function toggleValue(value: string, values: string[], setValues: (next: string[]) => void) {
    setValues(values.includes(value) ? values.filter((item) => item !== value) : [...values, value]);
  }

  async function submit() {
    setError("");
    try {
      await onAuthorize({
        username,
        account_number: accountNumber,
        otp_code: otpCode,
        scopes,
        selected_account_ids: selectedAccountIds,
      });
    } catch (nextError) {
      setError(getApiErrorMessage(nextError, "Unable to authorize this connection."));
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 py-8 backdrop-blur-sm">
      <section aria-modal="true" className="glass-panel max-h-full w-full max-w-2xl overflow-y-auto p-6" role="dialog">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="eyebrow">Grant consent</p>
            <h2 className="mt-2 text-xl font-semibold text-white">Connect to {initiation.provider.name}</h2>
            <p className="mt-1 text-xs font-semibold uppercase text-pink-200/65">{initiation.provider.type}</p>
          </div>
          <button aria-label="Close connection dialog" className="text-white/45 hover:text-white" disabled={loading} onClick={onClose} type="button">
            <X className="h-5 w-5" />
          </button>
        </div>

        <p className="mt-5 text-sm leading-6 text-white/55">
          {isMockBank
            ? "This is a simulated bank authorization flow. Use demo credentials to grant Velora access to selected mock accounts."
            : "This sandbox connection uses test credentials and simulated consent. No real bank data or real money is used."}
        </p>

        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <label className="grid gap-1.5 text-xs font-semibold text-white/65">
            Username or customer ID
            <input className="form-control" onChange={(event) => setUsername(event.target.value)} placeholder={isMockBank ? "demo" : "Sandbox test ID"} value={username} />
            {isMockBank && <span className="font-normal text-white/35">Demo username: demo</span>}
          </label>
          <label className="grid gap-1.5 text-xs font-semibold text-white/65">
            Account number <span className="font-normal text-white/35">(optional)</span>
            <input className="form-control" onChange={(event) => setAccountNumber(event.target.value)} placeholder="Optional identifier" value={accountNumber} />
          </label>
          <label className="grid gap-1.5 text-xs font-semibold text-white/65">
            OTP code
            <input className="form-control" inputMode="numeric" onChange={(event) => setOtpCode(event.target.value)} value={otpCode} />
            <span className="font-normal text-white/35">Demo OTP: 123456</span>
          </label>
        </div>

        <div className="mt-6">
          <h3 className="text-sm font-semibold text-white">Consent scopes</h3>
          <p className="mt-1 text-xs text-white/40">Choose what Velora can read from this provider.</p>
          <div className="mt-3 grid gap-2 sm:grid-cols-3">
            {initiation.available_scopes.map((scope) => (
              <label className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.035] px-3 py-2.5 text-xs text-white/70" key={scope}>
                <input checked={scopes.includes(scope)} onChange={() => toggleValue(scope, scopes, setScopes)} type="checkbox" />
                {scope}
              </label>
            ))}
          </div>
        </div>

        {initiation.available_accounts.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-white">Accounts to share</h3>
            <div className="mt-3 grid gap-2">
              {initiation.available_accounts.map((account) => (
                <label className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/[0.035] px-3 py-3 text-sm text-white/70" key={account.external_account_id}>
                  <input checked={selectedAccountIds.includes(account.external_account_id)} onChange={() => toggleValue(account.external_account_id, selectedAccountIds, setSelectedAccountIds)} type="checkbox" />
                  <span>{account.account_name} <span className="text-xs text-white/35">({account.account_type}, {account.currency})</span></span>
                </label>
              ))}
            </div>
          </div>
        )}

        {error && <p className="mt-5 rounded-lg border border-red-300/20 bg-red-300/[0.06] px-3 py-2.5 text-sm text-red-100">{error}</p>}

        <div className="mt-6 flex justify-end gap-3">
          <button className="button-secondary" disabled={loading} onClick={onClose} type="button">Cancel</button>
          <button className="button-primary" disabled={loading} onClick={submit} type="button">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShieldCheck className="h-4 w-4" />}
            {isMockBank ? "Authorize with mock bank" : "Authorize sandbox connection"}
          </button>
        </div>
      </section>
    </div>
  );
}

export default function OpenBankingPage() {
  const [providers, setProviders] = useState<BankProvider[]>([]);
  const [connections, setConnections] = useState<BankConnection[]>([]);
  const [activeProvider, setActiveProvider] = useState("");
  const [initiation, setInitiation] = useState<ConnectionInitiation | null>(null);
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
      setInitiation(await initiateProviderConnection(providerCode));
    } catch (error) {
      setMessage(getApiErrorMessage(error, "Unable to start this connection."));
    } finally {
      setActiveProvider("");
    }
  }

  async function authorize(values: {
    username: string;
    account_number: string;
    otp_code: string;
    scopes: string[];
    selected_account_ids: string[];
  }) {
    if (!initiation) return;
    setActiveProvider(initiation.provider.code);
    setMessage("");
    try {
      const result = await authorizeProviderConnection({ provider_code: initiation.provider.code, ...values });
      setMessage(`${result.connection.provider_name} is connected. Sync to import account activity.`);
      setInitiation(null);
      setConnections(await getConnections());
    } catch (error) {
      throw error;
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

  async function disconnect(providerCode: string) {
    if (!window.confirm("Disconnect this provider? Existing imported transactions will remain in Velora.")) return;
    setActiveProvider(providerCode);
    setMessage("");
    try {
      await disconnectProvider(providerCode);
      setMessage("Provider disconnected. Existing imported transactions remain available.");
      setConnections(await getConnections());
    } catch (error) {
      setMessage(getApiErrorMessage(error, "Unable to disconnect this provider."));
    } finally {
      setActiveProvider("");
    }
  }

  return (
    <div className="grid gap-7">
      <PageHeader
        description="Grant scoped consent, then sync balances and transaction activity through a provider adapter."
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
                  connection={connections.find((connection) => connection.provider_code === provider.code && connection.status === "connected")}
                  key={provider.code}
                  loading={activeProvider === provider.code}
                  onConnect={() => connect(provider.code)}
                  onDisconnect={() => disconnect(provider.code)}
                  onSync={() => sync(provider.code)}
                  provider={provider}
                />
              ))}
            </div>
          </section>
        );
      })}

      <section className="glass-subtle px-4 py-3 text-xs leading-6 text-white/38">
        Every provider is selected through the same banking adapter registry. {connections.filter((connection) => connection.status === "connected").length} provider{connections.filter((connection) => connection.status === "connected").length === 1 ? " is" : "s are"} connected to this profile.
      </section>

      {initiation && (
        <ConnectionModal
          initiation={initiation}
          loading={activeProvider === initiation.provider.code}
          onAuthorize={authorize}
          onClose={() => setInitiation(null)}
        />
      )}
    </div>
  );
}
