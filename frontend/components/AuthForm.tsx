"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { KeyRound, Loader2, LogIn, UserPlus } from "lucide-react";
import { getApiErrorMessage } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";

type AuthMode = "login" | "signup";

type AuthFormProps = {
  defaultMode?: AuthMode;
  onSuccess?: () => void;
  showDemo?: boolean;
  fixedMode?: boolean;
};

function authMessage(error: unknown) {
  const message = getApiErrorMessage(error, "Unable to authenticate this account.");
  if (message === "Invalid email or password") return "The email or password is incorrect.";
  if (message === "Email already registered") return "This email is already registered.";
  if (message.includes("at least 8")) return "Your password needs at least 8 characters.";
  return message;
}

export function AuthForm({
  defaultMode = "login",
  onSuccess,
  showDemo = true,
  fixedMode = false,
}: AuthFormProps) {
  const auth = useAuth();
  const [mode, setMode] = useState<AuthMode>(defaultMode);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const loading = auth.status === "loading";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (mode === "signup" && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      if (mode === "signup") {
        await auth.signup({ full_name: fullName.trim(), email: email.trim(), password });
      } else {
        await auth.login({ email: email.trim(), password });
      }
      onSuccess?.();
    } catch (nextError) {
      setError(authMessage(nextError));
    }
  }

  async function useDemoAccount() {
    setError("");
    try {
      await auth.demoLogin();
      onSuccess?.();
    } catch (nextError) {
      setError(authMessage(nextError));
    }
  }

  return (
    <div className="grid gap-4">
      {!fixedMode && <div className="grid grid-cols-2 rounded-lg border border-white/10 bg-black/20 p-1 text-sm font-medium">
        <button
          className={`inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 transition ${
            mode === "login" ? "bg-white/10 text-white shadow-sm" : "text-white/45"
          }`}
          disabled={loading}
          onClick={() => setMode("login")}
          type="button"
        >
          <LogIn className="h-4 w-4" aria-hidden="true" />
          Login
        </button>
        <button
          className={`inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 transition ${
            mode === "signup" ? "bg-white/10 text-white shadow-sm" : "text-white/45"
          }`}
          disabled={loading}
          onClick={() => setMode("signup")}
          type="button"
        >
          <UserPlus className="h-4 w-4" aria-hidden="true" />
          Signup
        </button>
      </div>}

      <form className="grid gap-3" onSubmit={submit}>
        {mode === "signup" && (
          <label className="grid gap-2 text-sm font-medium text-white/62">
            Full name
            <input
              autoComplete="name"
              className="form-control font-normal"
              onChange={(event) => setFullName(event.target.value)}
              required
              value={fullName}
            />
          </label>
        )}
        <label className="grid gap-2 text-sm font-medium text-white/62">
          Email
          <input
            autoComplete="email"
            className="form-control font-normal"
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
        </label>
        <label className="grid gap-2 text-sm font-medium text-white/62">
          Password
          <input
            autoComplete={mode === "signup" ? "new-password" : "current-password"}
            className="form-control font-normal"
            minLength={8}
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
        </label>
        {mode === "signup" && (
          <label className="grid gap-2 text-sm font-medium text-white/62">
            Confirm password
            <input
              autoComplete="new-password"
              className="form-control font-normal"
              minLength={8}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              type="password"
              value={confirmPassword}
            />
          </label>
        )}

        {error && (
          <p className="rounded-lg border border-red-300/20 bg-red-300/[0.08] px-3 py-2 text-sm text-red-200">
            {error}
          </p>
        )}

        <button
          className="button-primary mt-1"
          disabled={loading}
          type="submit"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <LogIn className="h-4 w-4" aria-hidden="true" />}
          {mode === "signup" ? "Create account" : "Sign in"}
        </button>
      </form>

      {showDemo && (
        <button
          className="button-secondary"
          disabled={loading}
          onClick={useDemoAccount}
          type="button"
        >
          <KeyRound className="h-4 w-4" aria-hidden="true" />
          Use demo account
        </button>
      )}
      {fixedMode && (
        <p className="text-center text-sm text-white/42">
          {mode === "signup" ? "Already have an account?" : "New to Velora?"}{" "}
          <Link className="font-semibold text-pink-300 hover:text-pink-200" href={mode === "signup" ? "/login" : "/signup"}>
            {mode === "signup" ? "Log in" : "Create an account"}
          </Link>
        </p>
      )}
    </div>
  );
}
