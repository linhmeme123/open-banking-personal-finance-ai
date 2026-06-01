"use client";

import { FormEvent, useEffect, useState } from "react";
import { Bot, Loader2, SendHorizontal, UserRound } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { apiGet, apiPost, getApiErrorMessage } from "@/lib/api";

type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

export default function AiCoachPage() {
  const [message, setMessage] = useState("How is my spending looking this month?");
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [provider, setProvider] = useState("rule_based");

  async function loadHistory() {
    setHistory(await apiGet<ChatMessage[]>("/api/ai/chat/history"));
  }

  async function askCoach(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!message.trim()) return;
    setLoading(true);
    setError("");
    try {
      const response = await apiPost<{ answer: string; provider: string }>("/api/ai/chat", { message: message.trim() });
      setProvider(response.provider);
      await loadHistory();
      setMessage("");
    } catch (nextError) {
      setError(getApiErrorMessage(nextError, "Unable to reach the AI coach."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory().catch(() => setHistory([]));
  }, []);

  return (
    <div className="grid gap-6">
      <PageHeader
        description="Ask questions grounded in your synced transactions, budgets, and recurring payments."
        eyebrow="Personalized guidance"
        title="AI Coach"
      />
      <p className="-mt-4 text-xs text-white/35">Powered by {provider}</p>

      <section className="glass-panel grid min-h-[520px] grid-rows-[1fr_auto] overflow-hidden">
        <div className="grid content-start gap-3 overflow-y-auto p-4 sm:p-5">
          {!history.length && (
            <div className="mx-auto max-w-sm py-16 text-center">
              <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-pink-300/10 text-pink-200">
                <Bot className="h-6 w-6" aria-hidden="true" />
              </span>
              <p className="mt-4 text-sm font-semibold text-white">Your AI coach is ready</p>
              <p className="mt-2 text-sm leading-6 text-white/38">Ask about cashflow, budgets, categories, or repeated spending.</p>
            </div>
          )}
          {history.map((item) => (
            <article
              className={`flex max-w-3xl gap-3 rounded-lg p-4 ${
                item.role === "assistant"
                  ? "border border-pink-300/10 bg-pink-300/[0.045]"
                  : "ml-auto border border-white/[0.08] bg-white/[0.055]"
              }`}
              key={item.id}
            >
              {item.role === "assistant" ? (
                <Bot className="mt-0.5 h-4 w-4 shrink-0 text-pink-300" aria-hidden="true" />
              ) : (
                <UserRound className="mt-0.5 h-4 w-4 shrink-0 text-cyan-300" aria-hidden="true" />
              )}
              <p className="text-sm leading-6 text-white/72">{item.content}</p>
            </article>
          ))}
        </div>

        <form className="border-t border-white/[0.08] bg-black/10 p-4" onSubmit={askCoach}>
          {error && <p className="mb-3 text-sm text-red-200">{error}</p>}
          <div className="flex gap-2">
            <input
              className="form-control"
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Ask your coach about this month's finances..."
              value={message}
            />
            <button aria-label="Send message" className="button-primary px-3.5" disabled={loading} title="Send message" type="submit">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <SendHorizontal className="h-4 w-4" aria-hidden="true" />}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
