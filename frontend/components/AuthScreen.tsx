"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { AuthForm } from "@/components/AuthForm";
import { AuthLayout } from "@/components/AuthLayout";
import { useAuth } from "@/components/AuthProvider";

export function AuthScreen({ mode }: { mode: "login" | "signup" }) {
  const router = useRouter();
  const { status } = useAuth();
  const signup = mode === "signup";

  useEffect(() => {
    if (status === "authenticated") {
      router.replace("/app");
    }
  }, [router, status]);

  return (
    <AuthLayout
      description={
        signup
          ? "Create your private workspace and start connecting your banking data."
          : "Welcome back. Sign in to return to your connected financial overview."
      }
      title={signup ? "Create your account" : "Log in to Velora"}
    >
      <AuthForm
        defaultMode={mode}
        fixedMode
        onSuccess={() => router.replace("/app")}
        showDemo={!signup}
      />
    </AuthLayout>
  );
}
