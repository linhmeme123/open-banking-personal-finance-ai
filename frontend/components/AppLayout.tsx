"use client";

import { ReactNode, useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { Sidebar } from "@/components/Sidebar";
import { TopBar } from "@/components/TopBar";

export function AppLayout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#08070b]">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div className="lg:pl-64">
          <TopBar onOpenSidebar={() => setSidebarOpen(true)} />
          <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8">{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
