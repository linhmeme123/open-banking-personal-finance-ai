"use client";

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { apiGet, apiPost, ApiError } from "@/lib/api";
import {
  AuthUser,
  clearSession,
  getStoredSession,
  SESSION_CHANGE_EVENT,
  StoredSession,
  storeSession,
} from "@/lib/session";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

type LoginInput = {
  email: string;
  password: string;
};

type SignupInput = LoginInput & {
  full_name: string;
};

type AuthContextValue = {
  status: AuthStatus;
  session: StoredSession | null;
  user: AuthUser | null;
  login: (input: LoginInput) => Promise<StoredSession>;
  signup: (input: SignupInput) => Promise<StoredSession>;
  demoLogin: () => Promise<StoredSession>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<AuthUser | null>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function readStoredAuth() {
  const session = getStoredSession();
  return {
    session,
    status: session ? "authenticated" : "unauthenticated",
  } as const;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [session, setSession] = useState<StoredSession | null>(null);

  const applySession = useCallback((nextSession: StoredSession | null) => {
    setSession(nextSession);
    setStatus(nextSession ? "authenticated" : "unauthenticated");
  }, []);

  const refreshUser = useCallback(async () => {
    const currentSession = getStoredSession();
    if (!currentSession) {
      applySession(null);
      return null;
    }

    try {
      const user = await apiGet<AuthUser>("/api/auth/me");
      const latestSession = getStoredSession() ?? currentSession;
      const nextSession = { ...latestSession, user };
      storeSession(nextSession);
      applySession(nextSession);
      return user;
    } catch {
      clearSession();
      applySession(null);
      return null;
    }
  }, [applySession]);

  useEffect(() => {
    const syncFromStorage = () => {
      const next = readStoredAuth();
      setSession(next.session);
      setStatus(next.status);
    };

    window.addEventListener(SESSION_CHANGE_EVENT, syncFromStorage);
    window.addEventListener("storage", syncFromStorage);

    const stored = getStoredSession();
    if (stored) {
      setSession(stored);
      refreshUser().finally(() => undefined);
    } else {
      setStatus("unauthenticated");
    }

    return () => {
      window.removeEventListener(SESSION_CHANGE_EVENT, syncFromStorage);
      window.removeEventListener("storage", syncFromStorage);
    };
  }, [refreshUser]);

  const login = useCallback(
    async (input: LoginInput) => {
      setStatus("loading");
      try {
        const nextSession = await apiPost<StoredSession>("/api/auth/login", input, undefined, {
          auth: false,
        });
        storeSession(nextSession);
        applySession(nextSession);
        return nextSession;
      } catch (error) {
        const stored = getStoredSession();
        applySession(stored);
        throw error;
      }
    },
    [applySession],
  );

  const signup = useCallback(
    async (input: SignupInput) => {
      setStatus("loading");
      try {
        const nextSession = await apiPost<StoredSession>("/api/auth/signup", input, undefined, {
          auth: false,
        });
        storeSession(nextSession);
        applySession(nextSession);
        return nextSession;
      } catch (error) {
        const stored = getStoredSession();
        applySession(stored);
        throw error;
      }
    },
    [applySession],
  );

  const demoLogin = useCallback(async () => {
    const credentials = {
      email: "demo@example.com",
      password: "demo-password",
    };

    try {
      return await signup({ full_name: "Demo User", ...credentials });
    } catch (error) {
      if (error instanceof ApiError && error.status !== 400) throw error;
      return login(credentials);
    }
  }, [login, signup]);

  const logout = useCallback(async () => {
    const activeToken = getStoredSession()?.access_token;
    try {
      if (activeToken) {
        await apiPost<{ message: string }>("/api/auth/logout", {}, activeToken);
      }
    } finally {
      clearSession();
      applySession(null);
    }
  }, [applySession]);

  const value = useMemo(
    () => ({
      status,
      session,
      user: session?.user ?? null,
      login,
      signup,
      demoLogin,
      logout,
      refreshUser,
    }),
    [demoLogin, login, logout, refreshUser, session, signup, status],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
