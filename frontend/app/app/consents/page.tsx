"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/PageHeader";
import { apiGet } from "@/lib/api";

type Consent = {
  id: number;
  provider_code: string;
  scope: string;
  action: string;
  event_hash: string;
  created_at: string;
};

export default function ConsentsPage() {
  const [consents, setConsents] = useState<Consent[]>([]);

  useEffect(() => {
    apiGet<Consent[]>("/api/consents").then(setConsents).catch(() => setConsents([]));
  }, []);

  return (
    <div className="grid gap-6">
      <PageHeader
        description="Review the append-only trail of permissions granted to connected banking providers."
        eyebrow="Audit trail"
        title="Consents"
      />

      <section className="glass-panel overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-white/[0.08] bg-white/[0.025] text-[10px] font-semibold uppercase text-white/35">
            <tr>
              <th className="px-5 py-4">Time</th>
              <th className="px-5 py-4">Provider</th>
              <th className="px-5 py-4">Action</th>
              <th className="px-5 py-4">Scope</th>
              <th className="px-5 py-4">Event hash</th>
            </tr>
          </thead>
          <tbody>
            {consents.map((consent) => (
              <tr className="border-b border-white/[0.06] last:border-0" key={consent.id}>
                <td className="px-5 py-4 text-white/42">{new Date(consent.created_at).toLocaleString("en-US")}</td>
                <td className="px-5 py-4 font-medium text-white">{consent.provider_code}</td>
                <td className="px-5 py-4">
                  <span className="rounded-full border border-emerald-300/15 bg-emerald-300/[0.07] px-2.5 py-1 text-xs text-emerald-200">
                    {consent.action}
                  </span>
                </td>
                <td className="px-5 py-4 text-white/48">{consent.scope}</td>
                <td className="max-w-52 truncate px-5 py-4 font-mono text-xs text-white/32">{consent.event_hash}</td>
              </tr>
            ))}
            {!consents.length && (
              <tr>
                <td className="px-5 py-8 text-white/42" colSpan={5}>No consent events have been recorded yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
