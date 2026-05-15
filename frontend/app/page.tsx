import Link from "next/link";

export default function HomePage() {
  return (
    <div className="grid gap-8">
      <section className="rounded-3xl bg-white p-8 shadow-sm">
        <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Fintech Portfolio Project
        </p>
        <h1 className="max-w-3xl text-4xl font-bold tracking-tight">
          Open Banking Personal Finance AI
        </h1>
        <p className="mt-4 max-w-2xl text-slate-600">
          Ứng dụng quản lý tài chính cá nhân dùng dữ liệu Open Banking giả lập,
          AI phân loại giao dịch, dashboard dòng tiền và AI financial coach.
        </p>
        <div className="mt-6 flex gap-3">
          <Link href="/dashboard" className="rounded-xl bg-slate-900 px-5 py-3 text-white">
            Mở Dashboard
          </Link>
          <Link href="/chat" className="rounded-xl border px-5 py-3">
            Hỏi AI Coach
          </Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          ["Open Banking", "Kết nối account/transaction từ provider giả lập."],
          ["AI Categorization", "Tự động phân loại giao dịch theo merchant/description."],
          ["Personal Finance Coach", "Chatbot phân tích chi tiêu và gợi ý tiết kiệm."]
        ].map(([title, desc]) => (
          <div key={title} className="rounded-2xl border bg-white p-5 shadow-sm">
            <h2 className="font-semibold">{title}</h2>
            <p className="mt-2 text-sm text-slate-600">{desc}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
