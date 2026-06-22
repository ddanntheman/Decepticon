"use client";

interface IconProps {
  name: string;
  size?: number;
  className?: string;
  style?: React.CSSProperties;
}

export default function Icon({ name, size = 24, className, style }: IconProps) {
  const props = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.5,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    className,
    style,
    "aria-hidden": true as const,
  };

  switch (name) {
    case "heart":
      return (
        <svg {...props}>
          <path d="M12 20s-7-4.5-7-10.5A4.5 4.5 0 0 1 12 6a4.5 4.5 0 0 1 7 3.5C19 15.5 12 20 12 20z" />
        </svg>
      );
    case "converge":
      return (
        <svg {...props}>
          <path d="M4 4l8 8M20 4l-8 8M12 12v8" />
          <circle cx="12" cy="12" r="2" />
        </svg>
      );
    case "tree":
      return (
        <svg {...props}>
          <path d="M12 21v-7" />
          <path d="M12 14L7 9M12 14l5-5" />
          <path d="M12 14V4" />
          <circle cx="12" cy="3.5" r="1.5" />
          <circle cx="7" cy="8.5" r="1.5" />
          <circle cx="17" cy="8.5" r="1.5" />
        </svg>
      );
    case "shield-check":
      return (
        <svg {...props}>
          <path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z" />
          <path d="M9 12l2 2 4-4" />
        </svg>
      );
    case "seal":
      return (
        <svg {...props}>
          <path d="M12 2l2.4 1.7 2.9-.4 1.1 2.7 2.4 1.7-.6 2.8 1 2.7-2.2 1.9-.4 2.9-2.9.5-1.8 2.3L12 19l-2.4 1.7-2.9-.4-1.1-2.7L3.2 16l.6-2.8-1-2.7 2.2-1.9.4-2.9 2.9-.5 1.8-2.3L12 2z" />
          <path d="M9 12l2 2 4-4" />
        </svg>
      );
    case "transparency":
      return (
        <svg {...props}>
          <rect x="3" y="5" width="18" height="14" rx="2" />
          <path d="M3 10h18" />
          <path d="M8 15h2M14 15h2" />
        </svg>
      );
    case "menu":
      return (
        <svg {...props}>
          <path d="M4 7h16M4 12h16M4 17h16" />
        </svg>
      );
    case "close":
      return (
        <svg {...props}>
          <path d="M6 6l12 12M18 6L6 18" />
        </svg>
      );
    case "play":
      return (
        <svg {...props} fill="currentColor" stroke="none">
          <path d="M8 5v14l11-7z" />
        </svg>
      );
    case "arrow-right":
      return (
        <svg {...props}>
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      );
    case "arrow-long":
      return (
        <svg
          {...props}
          width={48}
          height={24}
          viewBox="0 0 48 24"
        >
          <path d="M2 12h44M38 4l8 8-8 8" />
        </svg>
      );
    case "facebook":
      return (
        <svg {...props}>
          <path d="M16 8.5h-2.5A1.5 1.5 0 0 0 12 10v2h4l-.5 3H12v7h-3v-7H6v-3h3v-2.5A4.5 4.5 0 0 1 13.5 5H16v3.5z" />
        </svg>
      );
    case "twitter":
      return (
        <svg {...props}>
          <path d="M22 5.8a8 8 0 0 1-2.4.7 4 4 0 0 0 1.8-2.3 8 8 0 0 1-2.6 1 4 4 0 0 0-6.9 3.6A11.4 11.4 0 0 1 3 4.7a4 4 0 0 0 1.3 5.4 4 4 0 0 1-1.9-.5v.1a4 4 0 0 0 3.3 4 4 4 0 0 1-1.9.1 4 4 0 0 0 3.8 2.8A8 8 0 0 1 2 18.3 11.4 11.4 0 0 0 8.2 20c7.5 0 11.6-6.2 11.6-11.6v-.5A8.3 8.3 0 0 0 22 5.8z" />
        </svg>
      );
    case "instagram":
      return (
        <svg {...props}>
          <rect x="3" y="3" width="18" height="18" rx="5" />
          <circle cx="12" cy="12" r="4" />
          <circle cx="17.5" cy="6.5" r="1" fill="currentColor" />
        </svg>
      );
    case "youtube":
      return (
        <svg {...props}>
          <rect x="2.5" y="6" width="19" height="12" rx="3" />
          <path
            d="M10 9.5v5l4.5-2.5L10 9.5z"
            fill="currentColor"
          />
        </svg>
      );
    default:
      return null;
  }
}
