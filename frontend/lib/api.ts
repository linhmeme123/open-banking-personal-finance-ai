import {
  clearSession,
  getAccessToken,
  getRefreshToken,
  getStoredSession,
  storeSession,
  StoredSession,
} from "@/lib/session";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

type ApiRequestOptions = {
  auth?: boolean;
  retryAuth?: boolean;
};

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(formatApiErrorDetail(detail) || `API error: ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function formatApiErrorDetail(detail: unknown): string {
  if (!detail) return "";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object" && "msg" in item) return String(item.msg);
        return "";
      })
      .filter(Boolean)
      .join(" ");
  }
  if (typeof detail === "object" && "message" in detail) {
    return String((detail as { message: unknown }).message);
  }
  return "";
}

export function getApiErrorMessage(error: unknown, fallback = "Request failed"): string {
  if (error instanceof ApiError) return error.message || fallback;
  if (error instanceof Error) return error.message || fallback;
  return fallback;
}

function authHeaders(token?: string, auth = true): HeadersInit {
  if (!auth) return {};
  const resolvedToken = token || getAccessToken();
  return resolvedToken ? { Authorization: `Bearer ${resolvedToken}` } : {};
}

async function readError(response: Response): Promise<ApiError> {
  try {
    const data = await response.json();
    return new ApiError(response.status, data.detail ?? data);
  } catch {
    return new ApiError(response.status, response.statusText);
  }
}

async function refreshStoredSession(): Promise<string | null> {
  const session = getStoredSession();
  const refreshToken = session?.refresh_token || getRefreshToken();
  if (!refreshToken) {
    clearSession();
    return null;
  }

  const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    clearSession();
    return null;
  }

  const nextSession = (await response.json()) as StoredSession;
  storeSession(nextSession);
  return nextSession.access_token;
}

async function apiRequest<T>(
  path: string,
  init: RequestInit,
  token?: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const auth = options.auth ?? true;
  const retryAuth = options.retryAuth ?? true;
  const headers = {
    ...(init.headers ?? {}),
    ...authHeaders(token, auth),
  };

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  if (response.status === 401 && auth && retryAuth) {
    const refreshedToken = await refreshStoredSession();
    if (refreshedToken) {
      return apiRequest<T>(path, init, refreshedToken, { auth, retryAuth: false });
    }
  }

  if (!response.ok) throw await readError(response);
  if (response.status === 204) return undefined as T;
  return response.json();
}

export async function apiGet<T>(
  path: string,
  token?: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  return apiRequest<T>(path, { cache: "no-store" }, token, options);
}

export async function apiPost<T>(
  path: string,
  body?: unknown,
  token?: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  return apiRequest<T>(
    path,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body ?? {}),
    },
    token,
    options,
  );
}
