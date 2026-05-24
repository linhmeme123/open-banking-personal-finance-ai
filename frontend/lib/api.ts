const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

function authHeaders(token?: string): HeadersInit {
  const resolvedToken =
    token || (typeof window !== "undefined" ? window.localStorage.getItem("pfai_token") || "" : "");
  return resolvedToken ? { Authorization: `Bearer ${resolvedToken}` } : {};
}

export async function apiGet<T>(path: string, token?: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function apiPost<T>(path: string, body?: unknown, token?: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(body ?? {}),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
