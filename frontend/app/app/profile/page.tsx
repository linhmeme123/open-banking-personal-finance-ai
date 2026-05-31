"use client";

import { ChangeEvent, FormEvent, useState } from "react";
import { Camera, KeyRound, Loader2, LogOut, Mail, UserRound } from "lucide-react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/Card";
import { PageHeader } from "@/components/PageHeader";
import { UserAvatar } from "@/components/UserAvatar";
import { useAuth } from "@/components/AuthProvider";
import { storeAvatar } from "@/lib/session";

export default function ProfilePage() {
  const router = useRouter();
  const { logout, status, user } = useAuth();
  const [passwordMessage, setPasswordMessage] = useState("");

  function selectAvatar(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => storeAvatar(String(reader.result ?? ""));
    reader.readAsDataURL(file);
  }

  async function signOut() {
    await logout();
    router.replace("/");
  }

  function submitPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // TODO: Connect this form when the backend exposes a change-password endpoint.
    setPasswordMessage("Password updates are not available in the current API yet.");
  }

  return (
    <div className="grid gap-6">
      <PageHeader
        description="Manage your personal details, local avatar, and account security."
        eyebrow="Account settings"
        title="Profile"
      />

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(320px,0.72fr)]">
        <Card title="Personal information">
          <div className="flex flex-wrap items-center gap-5 border-b border-white/[0.08] pb-5">
            <UserAvatar name={user?.full_name} size="lg" />
            <div>
              <p className="text-lg font-semibold text-white">{user?.full_name}</p>
              <p className="mt-1 text-sm text-white/42">{user?.email}</p>
              <label className="button-secondary mt-4 cursor-pointer px-3 py-2">
                <Camera className="h-4 w-4" aria-hidden="true" />
                Change avatar
                <input accept="image/*" className="hidden" onChange={selectAvatar} type="file" />
              </label>
            </div>
          </div>

          <dl className="mt-5 grid gap-4 sm:grid-cols-2">
            <div className="glass-subtle p-4">
              <dt className="flex items-center gap-2 text-xs font-semibold uppercase text-white/35">
                <UserRound className="h-4 w-4 text-pink-300" aria-hidden="true" />
                Full name
              </dt>
              <dd className="mt-3 text-sm font-medium text-white">{user?.full_name}</dd>
            </div>
            <div className="glass-subtle p-4">
              <dt className="flex items-center gap-2 text-xs font-semibold uppercase text-white/35">
                <Mail className="h-4 w-4 text-cyan-300" aria-hidden="true" />
                Email
              </dt>
              <dd className="mt-3 truncate text-sm font-medium text-white">{user?.email}</dd>
            </div>
          </dl>

          <button className="button-secondary mt-5" disabled={status === "loading"} onClick={signOut} type="button">
            {status === "loading" ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <LogOut className="h-4 w-4" aria-hidden="true" />}
            Log out
          </button>
        </Card>

        <Card title="Change password">
          <form className="grid gap-3" onSubmit={submitPassword}>
            <label className="grid gap-2 text-sm font-medium text-white/58">
              Current password
              <input autoComplete="current-password" className="form-control" required type="password" />
            </label>
            <label className="grid gap-2 text-sm font-medium text-white/58">
              New password
              <input autoComplete="new-password" className="form-control" minLength={8} required type="password" />
            </label>
            <label className="grid gap-2 text-sm font-medium text-white/58">
              Confirm password
              <input autoComplete="new-password" className="form-control" minLength={8} required type="password" />
            </label>
            <button className="button-primary mt-1" type="submit">
              <KeyRound className="h-4 w-4" aria-hidden="true" />
              Update password
            </button>
            {passwordMessage && <p className="text-xs leading-5 text-amber-200/75">{passwordMessage}</p>}
          </form>
        </Card>
      </section>
    </div>
  );
}
