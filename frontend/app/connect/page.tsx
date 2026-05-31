import { redirect } from "next/navigation";

export default function LegacyConnectPage() {
  redirect("/app/open-banking");
}
