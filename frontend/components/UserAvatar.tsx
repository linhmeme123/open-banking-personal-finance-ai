"use client";

type UserAvatarProps = {
  name?: string | null;
  avatarUrl?: string | null;
  size?: "sm" | "md" | "lg";
};

const sizeClasses = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-20 w-20 text-xl",
};

export function UserAvatar({
  name = "User",
  avatarUrl,
  size = "md",
}: UserAvatarProps) {
  const displayName = name || "User";

  const initials = displayName
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

  const avatarSrc = avatarUrl
    ? avatarUrl.startsWith("http")
      ? avatarUrl
      : `${apiBaseUrl}${avatarUrl}`
    : "";

  if (avatarSrc) {
    return (
      <img
        alt={`${displayName} avatar`}
        className={`${sizeClasses[size]} shrink-0 rounded-full border border-pink-300/30 object-cover`}
        src={avatarSrc}
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