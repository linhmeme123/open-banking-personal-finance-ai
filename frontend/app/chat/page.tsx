"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import { demoLogin, getStoredSession } from "@/lib/session";

type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

export default function ChatPage() {
  const [message, setMessage] = useState("Tháng này tôi đang chi tiêu như thế nào?");
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  async function activeToken() {
    const stored = getStoredSession();
    if (stored) return stored.access_token;
    const nextSession = await demoLogin();
    return nextSession.access_token;
  }

  async function loadHistory() {
    const stored = getStoredSession();
    if (!stored) return;
    setHistory(await apiGet<ChatMessage[]>("/api/ai/chat/history", stored.access_token));
  }

  async function askCoach() {
    setLoading(true);
    try {
      const token = await activeToken();
      await apiPost<{ answer: string }>("/api/ai/chat", { message }, token);
      setHistory(await apiGet<ChatMessage[]>("/api/ai/chat/history", token));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory().catch(() => setHistory([]));
  }, []);

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">AI Financial Coach</h1>
        <p className="mt-2 text-slate-600">Ask about cashflow, categories, budgets, and recurring payments.</p>
      </div>

      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <textarea
          className="min-h-32 w-full rounded-lg border p-4 outline-none focus:ring-2 focus:ring-slate-300"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
        />
        <button
          onClick={askCoach}
          disabled={loading}
          className="mt-4 rounded-lg bg-slate-900 px-5 py-3 text-white disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Ask AI"}
        </button>
      </section>

      <section className="grid gap-3">
        {history.map((item) => (
          <div
            key={item.id}
            className={`rounded-lg border p-4 shadow-sm ${
              item.role === "assistant" ? "bg-white" : "bg-slate-900 text-white"
            }`}
          >
            <p className="mb-2 text-xs uppercase opacity-70">{item.role}</p>
            <p className="leading-7">{item.content}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
