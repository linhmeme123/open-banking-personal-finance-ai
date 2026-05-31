import { apiGet, apiPost } from "@/lib/api";

export const TRANSACTION_CATEGORIES = [
  "food",
  "groceries",
  "transport",
  "shopping",
  "salary",
  "transfer",
  "entertainment",
  "bills",
  "healthcare",
  "education",
  "investment",
  "unknown",
] as const;

export type ProviderType = "digital_bank" | "fintech" | "traditional_bank";

export type BankProvider = {
  code: string;
  name: string;
  type: ProviderType;
  logo_url: string | null;
  status: "available" | "coming_soon";
  supported_scopes: string[];
};

export type BankConnection = {
  id: number;
  provider_code: string;
  provider_name: string;
  provider_type: ProviderType;
  logo_url: string | null;
  status: string;
  consent_scope: string;
  last_synced_at: string | null;
};

export type Account = {
  id: number;
  account_name: string;
  account_type: string;
  currency: string;
  balance: number;
  provider_code: string;
  provider_name: string;
  provider_type: ProviderType;
};

export type FinanceTransaction = {
  id: number;
  transaction_time: string;
  description: string;
  merchant_name: string | null;
  amount: number;
  currency: string;
  direction: "income" | "expense";
  category: string | null;
  category_confidence: number | null;
  account_name: string;
  provider_code: string;
  provider_name: string;
  provider_type: ProviderType;
};

export type TransactionFilterValues = {
  provider_code: string;
  category: string;
  direction: string;
  date_from: string;
  date_to: string;
  min_amount: string;
  max_amount: string;
  search: string;
};

export const EMPTY_TRANSACTION_FILTERS: TransactionFilterValues = {
  provider_code: "",
  category: "",
  direction: "",
  date_from: "",
  date_to: "",
  min_amount: "",
  max_amount: "",
  search: "",
};

function buildQuery(values: Record<string, string>) {
  const params = new URLSearchParams();
  Object.entries(values).forEach(([key, value]) => {
    if (value.trim()) params.set(key, value.trim());
  });
  const query = params.toString();
  return query ? `?${query}` : "";
}

export function getProviders() {
  return apiGet<BankProvider[]>("/api/open-banking/providers", undefined, { auth: false });
}

export function getConnections() {
  return apiGet<BankConnection[]>("/api/open-banking/connections");
}

export function connectProvider(providerCode: string) {
  return apiPost<BankConnection>("/api/open-banking/connect", {
    provider_code: providerCode,
    scope: "accounts:read transactions:read balance:read",
  });
}

export function syncProvider(providerCode: string) {
  return apiPost<{ status: string; provider_code: string; created_accounts: number; created_transactions: number }>(
    "/api/open-banking/sync",
    { provider_code: providerCode },
  );
}

export function getAccounts(providerCode = "") {
  return apiGet<Account[]>(`/api/accounts${buildQuery({ provider_code: providerCode })}`);
}

export function getTransactions(filters: TransactionFilterValues) {
  return apiGet<FinanceTransaction[]>(`/api/transactions${buildQuery(filters)}`);
}

export function categorizeTransaction(transactionId: number) {
  return apiPost<{ transaction_id: number; category: string; confidence: number }>("/api/transactions/categorize", {
    transaction_id: transactionId,
  });
}

export function categorizeUncategorized(providerCode = "") {
  return apiPost<{ categorized_count: number }>("/api/transactions/categorize-all", {
    provider_code: providerCode || null,
  });
}
