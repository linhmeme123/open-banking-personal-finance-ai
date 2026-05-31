export const SESSION_CHANGE_EVENT = "pfai-session-change";
export const AVATAR_CHANGE_EVENT = "pfai-avatar-change";

const SESSION_KEY = "pfai_session";
const ACCESS_TOKEN_KEY = "pfai_token";
const REFRESH_TOKEN_KEY = "pfai_refresh_token";
const AVATAR_KEY = "pfai_avatar";

export type AuthUser = {
  id: number;
  full_name: string;
  email: string;
  is_active: boolean;
};

export type StoredSession = {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: AuthUser;
};

export function getStoredSession(): StoredSession | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredSession;
  } catch {
    clearTokens();
    return null;
  }
}

export function saveTokens(accessToken: string, refreshToken?: string) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  if (refreshToken) {
    window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  } else {
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
}

export function getAccessToken(): string {
  if (typeof window === "undefined") return "";
  return getStoredSession()?.access_token || window.localStorage.getItem(ACCESS_TOKEN_KEY) || "";
}

export function getRefreshToken(): string {
  if (typeof window === "undefined") return "";
  return getStoredSession()?.refresh_token || window.localStorage.getItem(REFRESH_TOKEN_KEY) || "";
}

export function clearTokens() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(SESSION_KEY);
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
}

function emitSessionChange() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(SESSION_CHANGE_EVENT));
}

export function storeSession(session: StoredSession) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  saveTokens(session.access_token, session.refresh_token);
  emitSessionChange();
}

export function clearSession() {
  if (typeof window === "undefined") return;
  clearTokens();
  emitSessionChange();
}

export function getStoredAvatar(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(AVATAR_KEY) || "";
}

export function storeAvatar(avatar: string) {
  if (typeof window === "undefined") return;
  if (avatar) {
    window.localStorage.setItem(AVATAR_KEY, avatar);
  } else {
    window.localStorage.removeItem(AVATAR_KEY);
  }
  window.dispatchEvent(new Event(AVATAR_CHANGE_EVENT));
}
