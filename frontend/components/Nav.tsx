import Link from "next/link";

const items = [
  { href: "/", label: "Home" },
  { href: "/connect", label: "Connect" },
  { href: "/accounts", label: "Accounts" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/transactions", label: "Transactions" },
  { href: "/budgets", label: "Budgets" },
  { href: "/insights", label: "Insights" },
  { href: "/consents", label: "Consents" },
  { href: "/chat", label: "AI Coach" },
];

export function Nav() {
  return (
    <nav className="border-b bg-white">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-4">
        <Link href="/" className="text-lg font-bold">
          Personal Finance AI
        </Link>
        <div className="flex flex-wrap gap-3 text-sm">
          {items.map((item) => (
            <Link key={item.href} className="text-slate-600 hover:text-slate-950" href={item.href}>
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
