import Link from "next/link";

const items = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/transactions", label: "Transactions" },
  { href: "/chat", label: "AI Coach" },
];

export function Nav() {
  return (
    <nav className="border-b bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-bold">
          Personal Finance AI
        </Link>
        <div className="flex gap-4 text-sm">
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
