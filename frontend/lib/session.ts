"use client";

import { apiPost } from "@/lib/api";

export type DemoUser = {
  id: number;
  full_name: string;
  email: string;
};

export type DemoSession = {
  access_token: string;
  refresh_token?: string;
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
  const credentials = {
    email: "demo@example.com",
    password: "demo-password",
  };
  let session: DemoSession;
  try {
    session = await apiPost<DemoSession>("/api/auth/signup", {
      full_name: "Demo User",
      ...credentials,
    });
  } catch {
    session = await apiPost<DemoSession>("/api/auth/login", credentials);
  }
  storeSession(session);
  return session;
}
