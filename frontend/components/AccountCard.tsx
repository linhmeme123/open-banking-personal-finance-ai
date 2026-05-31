import { CreditCard, Landmark, WalletCards } from "lucide-react";
import { formatCurrency } from "@/lib/format";
import { Account } from "@/lib/finance";

export function AccountCard({ account }: { account: Account }) {
  const Icon = account.account_type === "wallet" ? WalletCards : account.account_type === "savings" ? Landmark : CreditCard;

  return (
    <article className="glass-panel p-5">
      <div className="flex items-start justify-between gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-pink-300/10 text-pink-200">
          <Icon className="h-5 w-5" aria-hidden="true" />
        </span>
        <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[10px] font-semibold uppercase text-white/38">
          {account.account_type}
        </span>
      </div>
      <h3 className="mt-5 text-base font-semibold text-white">{account.account_name}</h3>
      <p className="mt-1 text-xs text-white/38">{account.provider_name}</p>
      <p className="mt-6 text-2xl font-semibold text-white">{formatCurrency(account.balance, account.currency)}</p>
    </article>
  );
}
