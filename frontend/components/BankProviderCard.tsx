import { Building2, Landmark, Loader2, RefreshCw, ShieldCheck, Smartphone } from "lucide-react";
import { BankConnection, BankProvider, ProviderType } from "@/lib/finance";

const TYPE_LABELS: Record<ProviderType, string> = {
  mock_bank: "Mock bank",
  sandbox: "Public sandbox",
  real_partner: "Real partner",
};

function ProviderIcon({ type }: { type: ProviderType }) {
  if (type === "sandbox") return <Smartphone className="h-5 w-5" aria-hidden="true" />;
  if (type === "real_partner") return <Landmark className="h-5 w-5" aria-hidden="true" />;
  return <Building2 className="h-5 w-5" aria-hidden="true" />;
}

export function BankProviderCard({
  provider,
  connection,
  loading,
  onConnect,
  onSync,
}: {
  provider: BankProvider;
  connection?: BankConnection;
  loading: boolean;
  onConnect: () => void;
  onSync: () => void;
}) {
  const unavailable = provider.status !== "available";
  const synced = Boolean(connection?.last_synced_at);
  const badge = unavailable ? "Coming soon" : synced ? "Synced" : connection ? "Connected" : "Available";

  return (
    <article className="glass-panel flex min-h-[248px] flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <span className="flex h-11 w-11 items-center justify-center rounded-lg border border-pink-300/15 bg-pink-300/[0.07] text-pink-200">
          <ProviderIcon type={provider.type} />
        </span>
        <span className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase ${connection ? "border-emerald-300/20 bg-emerald-300/[0.08] text-emerald-200" : "border-white/10 bg-white/[0.04] text-white/38"}`}>
          {badge}
        </span>
      </div>
      <p className="mt-5 text-[11px] font-semibold uppercase text-pink-200/65">{TYPE_LABELS[provider.type]}</p>
      <h3 className="mt-1 text-base font-semibold text-white">{provider.name}</h3>
      <p className="mt-2 text-sm leading-6 text-white/42">
        {connection ? "Consent active. Sync to refresh balances and transaction activity." : "Connect through the provider adapter with scoped data access."}
      </p>

      <div className="mt-auto pt-5">
        {!connection && (
          <button className="button-primary w-full" disabled={loading || unavailable} onClick={onConnect} type="button">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <ShieldCheck className="h-4 w-4" aria-hidden="true" />}
            {unavailable ? "Coming soon" : "Connect"}
          </button>
        )}
        {connection && (
          <button className="button-secondary w-full" disabled={loading} onClick={onSync} type="button">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <RefreshCw className="h-4 w-4" aria-hidden="true" />}
            Sync activity
          </button>
        )}
      </div>
    </article>
  );
}
