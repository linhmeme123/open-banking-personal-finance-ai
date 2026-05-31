"use client";

import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { ReactNode, useEffect } from "react";
import { useAuth } from "@/components/AuthProvider";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { status } = useAuth();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [router, status]);

  if (status !== "authenticated") {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#08070b]">
        <div className="inline-flex items-center gap-3 text-sm text-white/55">
          <Loader2 className="h-5 w-5 animate-spin text-pink-400" aria-hidden="true" />
          Checking your session
        </div>
      </main>
    );
  }

  return <>{children}</>;
}
