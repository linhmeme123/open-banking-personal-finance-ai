"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { getStoredSession } from "@/lib/session";

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
    const session = getStoredSession();
    if (!session) return;
    apiGet<Consent[]>("/api/consents", session.access_token)
      .then(setConsents)
      .catch(() => setConsents([]));
  }, []);

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-3xl font-bold">Consent audit</h1>
        <p className="mt-2 text-slate-600">Hash-linked records of sandbox banking consent actions.</p>
      </div>

      <section className="overflow-hidden rounded-lg border bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="p-4">Time</th>
              <th className="p-4">Provider</th>
              <th className="p-4">Action</th>
              <th className="p-4">Hash</th>
            </tr>
          </thead>
          <tbody>
            {consents.map((consent) => (
              <tr key={consent.id} className="border-t">
                <td className="p-4">{new Date(consent.created_at).toLocaleString("vi-VN")}</td>
                <td className="p-4">{consent.provider_code}</td>
                <td className="p-4">{consent.action}</td>
                <td className="max-w-xs truncate p-4 font-mono text-xs">{consent.event_hash}</td>
              </tr>
            ))}
            {consents.length === 0 && (
              <tr>
                <td className="p-4 text-slate-600" colSpan={4}>
                  No consent events yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
