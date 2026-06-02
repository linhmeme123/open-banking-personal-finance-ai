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

export type ProviderType = "mock_bank" | "sandbox" | "real_partner";

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
  selected_account_ids: string[];
  last_synced_at: string | null;
  connected_accounts_count: number;
};

export type AuthorizationAccount = {
  external_account_id: string;
  account_name: string;
  account_type: string;
  currency: string;
};

export type ConnectionInitiation = {
  connection: BankConnection;
  provider: Pick<BankProvider, "code" | "name" | "type">;
  required_fields: string[];
  available_scopes: string[];
  available_accounts: AuthorizationAccount[];
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
  last_synced_at: string | null;
};

export type FinanceTransaction = {
  id: number;
  external_id: string;
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

export function initiateProviderConnection(providerCode: string) {
  return apiPost<ConnectionInitiation>("/api/open-banking/connect/initiate", { provider_code: providerCode });
}

export function authorizeProviderConnection(values: {
  provider_code: string;
  username: string;
  account_number: string;
  otp_code: string;
  scopes: string[];
  selected_account_ids: string[];
}) {
  return apiPost<{ connection: BankConnection; selected_accounts: string[] }>("/api/open-banking/connect/authorize", values);
}

export function disconnectProvider(providerCode: string) {
  return apiPost<{ status: string; provider_code: string }>("/api/open-banking/disconnect", {
    provider_code: providerCode,
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

export type MockBankAccount = {
  external_account_id: string;
  account_name: string;
  account_type: string;
  currency: string;
  balance: number;
  last_updated_at: string;
};

export type MockBankTransaction = {
  external_transaction_id: string;
  external_account_id: string;
  transaction_time: string;
  description: string;
  merchant_name: string | null;
  amount: number;
  currency: string;
  direction: "income" | "expense";
  category: string | null;
  balance_before: number;
  balance_after: number;
  webhook_status: "pending" | "delivered" | "failed";
  sync_status: "pending" | "synced" | "failed";
};

export type MockBankEvent = {
  event_type: string;
  message: string;
  created_at: string;
};

const publicApi = { auth: false };

export function getMockBankProviders() {
  return apiGet<BankProvider[]>("/api/mock-bank/providers", undefined, publicApi);
}

export function getMockBankAccounts(providerCode: string) {
  return apiGet<MockBankAccount[]>(`/api/mock-bank/accounts${buildQuery({ provider_code: providerCode })}`, undefined, publicApi);
}

export function createMockBankAccount(providerCode: string, accountName: string) {
  return apiPost<MockBankAccount>("/api/mock-bank/accounts", {
    provider_code: providerCode,
    account_name: accountName,
    account_type: "checking",
    currency: "VND",
    balance: 0,
  }, undefined, publicApi);
}

export function getMockBankTransactions(providerCode: string, externalAccountId = "") {
  return apiGet<MockBankTransaction[]>(
    `/api/mock-bank/transactions${buildQuery({ provider_code: providerCode, external_account_id: externalAccountId })}`,
    undefined,
    publicApi,
  );
}

export function createMockBankTransaction(body: {
  provider_code: string;
  external_account_id: string;
  description: string;
  merchant_name: string;
  amount: number;
  direction: string;
  category?: string;
  transaction_time?: string;
}) {
  return apiPost<MockBankTransaction>("/api/mock-bank/transactions", body, undefined, publicApi);
}

export function generateMockBankTransaction(providerCode: string, externalAccountId: string) {
  return apiPost<MockBankTransaction>("/api/mock-bank/transactions/generate", {
    provider_code: providerCode,
    external_account_id: externalAccountId,
  }, undefined, publicApi);
}

export function sendMockBankWebhook(providerCode: string, externalTransactionId: string) {
  return apiPost<{ status: string; transactions_added: number }>("/api/mock-bank/webhooks/send", {
    provider_code: providerCode,
    external_transaction_id: externalTransactionId,
  });
}

export function getMockBankTransactionEvents(providerCode: string, externalTransactionId: string) {
  return apiGet<MockBankEvent[]>(
    `/api/mock-bank/transactions/${externalTransactionId}/events${buildQuery({ provider_code: providerCode })}`,
    undefined,
    publicApi,
  );
}
