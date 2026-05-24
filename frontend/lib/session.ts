"use client";

import { apiPost } from "@/lib/api";

export type DemoUser = {
  id: number;
  full_name: string;
  email: string;
};

export type DemoSession = {
  access_token: string;
  token_type: string;
  user: DemoUser;
};

export function getStoredSession(): DemoSession | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem("pfai_session");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as DemoSession;
  } catch {
    window.localStorage.removeItem("pfai_session");
    window.localStorage.removeItem("pfai_token");
    return null;
  }
}

export function storeSession(session: DemoSession) {
  window.localStorage.setItem("pfai_session", JSON.stringify(session));
  window.localStorage.setItem("pfai_token", session.access_token);
}

export function clearSession() {
  window.localStorage.removeItem("pfai_session");
  window.localStorage.removeItem("pfai_token");
}

export async function demoLogin(): Promise<DemoSession> {
  const session = await apiPost<DemoSession>("/api/auth/demo-login");
  storeSession(session);
  return session;
}
