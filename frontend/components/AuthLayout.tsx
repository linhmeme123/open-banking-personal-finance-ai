import { ReactNode } from "react";
import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";
import { Brand } from "@/components/Brand";

export function AuthLayout({
  children,
  title,
  description,
}: {
  children: ReactNode;
  title: string;
  description: string;
}) {
  return (
    <main className="grid min-h-screen lg:grid-cols-[minmax(0,1fr)_minmax(420px,0.72fr)]">
      <section className="relative hidden overflow-hidden border-r border-white/[0.08] lg:block">
        <img
          alt=""
          className="absolute inset-0 h-full w-full object-cover object-center opacity-55"
          src="/images/fintech-hero.png"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-[#08070b]/95 via-[#08070b]/55 to-[#08070b]/30" />
        <div className="relative flex h-full max-w-xl flex-col justify-between p-10">
          <Brand />
          <div className="pb-8">
            <p className="eyebrow">Secure open banking</p>
            <p className="mt-4 text-4xl font-semibold leading-tight text-white">
              Your finances, connected with clarity.
            </p>
            <p className="mt-4 max-w-md text-sm leading-7 text-white/55">
              Bring every account into one private workspace and turn raw transactions into
              practical next steps.
            </p>
          </div>
        </div>
      </section>

      <section className="flex min-h-screen flex-col bg-[#0b090e] px-5 py-6 sm:px-10">
        <div className="flex items-center justify-between">
          <div className="lg:hidden">
            <Brand />
          </div>
          <Link className="ml-auto inline-flex items-center gap-2 text-sm text-white/45 hover:text-white" href="/">
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
            Back home
          </Link>
        </div>

        <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center py-10">
          <div className="mb-7">
            <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-lg border border-pink-300/20 bg-pink-400/10 text-pink-300">
              <ShieldCheck className="h-5 w-5" aria-hidden="true" />
            </div>
            <h1 className="text-3xl font-semibold text-white">{title}</h1>
            <p className="mt-2 text-sm leading-6 text-white/45">{description}</p>
          </div>
          {children}
        </div>
      </section>
    </main>
  );
}
