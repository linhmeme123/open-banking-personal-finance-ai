import { redirect } from "next/navigation";

export default function LegacyBudgetsPage() {
  redirect("/app/budgets");
}
