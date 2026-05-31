import { ReactNode } from "react";
import { AppLayout } from "@/components/AppLayout";

export default function ProtectedAppLayout({ children }: { children: ReactNode }) {
  return <AppLayout>{children}</AppLayout>;
}
