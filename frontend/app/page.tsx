"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { useEffect, useState } from "react";
import { Brand } from "@/components/Brand";

const valueLines = [
  "Connect all your bank accounts in one place",
  "Understand where your money goes",
  "Auto-categorize transactions with AI",
  "Get personal finance insights instantly",
  "Help you save money and reach your goals",
];

function RotatingValueLine() {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setActiveIndex((current) => (current + 1) % valueLines.length);
    }, 3400);

    return () => window.clearInterval(interval);
  }, []);

  return (
    <div className="relative mt-7 h-16 w-full max-w-2xl overflow-hidden sm:h-10">
      {valueLines.map((line, index) => (
        <p
          aria-hidden={activeIndex !== index}
          className={`absolute inset-x-0 text-base leading-7 text-white/60 transition-all duration-700 ease-out sm:text-lg ${
            activeIndex === index ? "translate-y-0 opacity-100" : "translate-y-3 opacity-0"
          }`}
          key={line}
        >
          {line}
        </p>
      ))}
    </div>
  );
}

export default function LandingPage() {
  return (
    <main className="relative flex min-h-screen overflow-hidden bg-[#08070b]">
      <div className="absolute left-1/2 top-[-18rem] h-[36rem] w-[36rem] -translate-x-1/2 rounded-full bg-fuchsia-700/20 blur-[120px]" />
      <div className="absolute bottom-[-16rem] left-[-12rem] h-[34rem] w-[34rem] rounded-full bg-pink-600/15 blur-[120px]" />
      <div className="absolute bottom-[-10rem] right-[-12rem] h-[30rem] w-[30rem] rounded-full bg-violet-700/15 blur-[120px]" />

      <section className="relative z-10 mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 py-5 sm:px-8">
        <header>
          <Brand title="Velora Finance" />
        </header>

        <div className="flex flex-1 items-center justify-center py-16">
          <div className="flex w-full flex-col items-center text-center">
            <p className="eyebrow tracking-[0.22em]">Open banking, personally finance management</p>
            <h1 className="mt-6 bg-gradient-to-br from-white via-pink-100 to-fuchsia-300 bg-clip-text text-5xl font-semibold leading-[1.04] tracking-[-0.04em] text-transparent sm:text-7xl lg:text-8xl">
              Velora Finance
            </h1>
            <RotatingValueLine />
            <Link className="button-primary mt-8 px-5 py-3" href="/app">
              Go to dashboard
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
