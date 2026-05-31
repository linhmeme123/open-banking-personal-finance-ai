"use client";

import Link from "next/link";
import { ArrowRight, Bot, Landmark, LineChart, ShieldCheck } from "lucide-react";
import { Brand } from "@/components/Brand";
import { useAuth } from "@/components/AuthProvider";

const benefits = [
  { icon: Landmark, title: "One view of every account", description: "Connect banking data and keep balances in focus." },
  { icon: LineChart, title: "Know where money moves", description: "See income, expenses, budgets, and spending patterns." },
  { icon: Bot, title: "Ask your AI coach", description: "Turn synced activity into practical financial decisions." },
];

export default function LandingPage() {
  const { status } = useAuth();
  const authenticated = status === "authenticated";

  return (
    <main className="min-h-screen bg-[#08070b]">
      <section className="relative flex min-h-[88vh] flex-col overflow-hidden border-b border-white/[0.08]">
        <img
          alt="Velora Finance dashboard preview"
          className="absolute inset-0 h-full w-full object-cover object-[58%_center] opacity-70"
          src="/images/fintech-hero.png"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-[#08070b] via-[#08070b]/90 to-[#08070b]/25" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#08070b] via-transparent to-[#08070b]/30" />

        <header className="relative z-10 mx-auto flex w-full max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
          <Brand />
          <div className="flex items-center gap-2">
            {!authenticated && (
              <Link className="hidden px-3 py-2 text-sm font-semibold text-white/60 hover:text-white sm:block" href="/login">
                Log in
              </Link>
            )}
            <Link className="button-primary" href={authenticated ? "/app" : "/signup"}>
              {authenticated ? "Open dashboard" : "Sign up"}
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
        </header>

        <div className="relative z-10 mx-auto flex w-full max-w-7xl flex-1 items-center px-5 pb-16 pt-10 sm:px-8">
          <div className="max-w-2xl">
            <p className="eyebrow">Open banking, personally understood</p>
            <h1 className="mt-5 text-5xl font-semibold leading-[1.06] text-white sm:text-6xl lg:text-7xl">
              Velora Finance
            </h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-white/58 sm:text-lg">
              A connected personal finance workspace for clearer cashflow, smarter budgets, and AI-guided next steps.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link className="button-primary px-5 py-3" href={authenticated ? "/app" : "/login"}>
                {authenticated ? "Go to overview" : "Log in"}
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
              {!authenticated && (
                <Link className="button-secondary px-5 py-3" href="/signup">
                  Create account
                </Link>
              )}
            </div>
            <div className="mt-10 flex flex-wrap gap-x-6 gap-y-3 text-xs font-semibold uppercase text-white/38">
              <span className="inline-flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-300" aria-hidden="true" />
                Secure consent
              </span>
              <span>Connected insights</span>
              <span>AI coaching</span>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-white/[0.08] bg-[#0b090e]">
        <div className="mx-auto grid max-w-7xl gap-px bg-white/[0.08] sm:grid-cols-3">
          {benefits.map(({ icon: Icon, title, description }) => (
            <div className="bg-[#0b090e] px-6 py-7 sm:px-8" key={title}>
              <Icon className="h-5 w-5 text-pink-300" aria-hidden="true" />
              <h2 className="mt-4 text-sm font-semibold text-white">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-white/42">{description}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
