"use client";

import { useEffect, useState } from "react";
import { AVATAR_CHANGE_EVENT, getStoredAvatar } from "@/lib/session";

type UserAvatarProps = {
  name?: string;
  size?: "sm" | "md" | "lg";
};

const sizeClasses = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-20 w-20 text-xl",
};

export function UserAvatar({ name = "User", size = "md" }: UserAvatarProps) {
  const [avatar, setAvatar] = useState("");

  useEffect(() => {
    const syncAvatar = () => setAvatar(getStoredAvatar());
    syncAvatar();
    window.addEventListener(AVATAR_CHANGE_EVENT, syncAvatar);
    window.addEventListener("storage", syncAvatar);
    return () => {
      window.removeEventListener(AVATAR_CHANGE_EVENT, syncAvatar);
      window.removeEventListener("storage", syncAvatar);
    };
  }, []);

  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  if (avatar) {
    return (
      <img
        alt={`${name} avatar`}
        className={`${sizeClasses[size]} shrink-0 rounded-full border border-pink-300/30 object-cover`}
        src={avatar}
      />
    );
  }

  return (
    <span
      className={`${sizeClasses[size]} flex shrink-0 items-center justify-center rounded-full border border-pink-300/30 bg-gradient-to-br from-pink-500/80 to-fuchsia-700/80 font-bold text-white`}
    >
      {initials || "U"}
    </span>
  );
}
