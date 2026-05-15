"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api";

export default function ChatPage() {
  const [message, setMessage] = useState("Tháng này tôi đang chi tiêu như thế nào?");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function askCoach() {
    setLoading(true);
    setAnswer("");
    try {
      const res = await apiPost<{ answer: string }>("/api/ai/chat", {
        user_id: 1,
        message,
      });
      setAnswer(res.answer);
    } catch {
      setAnswer("Không gọi được backend. Hãy kiểm tra FastAPI đang chạy ở port 8000.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">AI Financial Coach</h1>
        <p className="mt-2 text-slate-600">
          Hỏi AI về chi tiêu, dòng tiền và thói quen tài chính.
        </p>
      </div>

      <section className="rounded-2xl border bg-white p-6 shadow-sm">
        <textarea
          className="min-h-32 w-full rounded-xl border p-4 outline-none focus:ring-2 focus:ring-slate-300"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button
          onClick={askCoach}
          disabled={loading}
          className="mt-4 rounded-xl bg-slate-900 px-5 py-3 text-white disabled:opacity-50"
        >
          {loading ? "Đang phân tích..." : "Hỏi AI"}
        </button>
      </section>

      {answer && (
        <section className="rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="mb-3 font-semibold">Trả lời</h2>
          <p className="leading-7 text-slate-700">{answer}</p>
        </section>
      )}
    </div>
  );
}
