import { redirect } from "next/navigation";

export default function LegacyTransactionsPage() {
  redirect("/app/transactions");
}
