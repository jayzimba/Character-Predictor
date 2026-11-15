export default function BrandLogo({ compact = false, inverted = false, className = '' }) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${className}`}>
      <svg
        className="logo-mark h-8 w-8 shrink-0"
        viewBox="0 0 64 64"
        role="img"
        aria-hidden={compact ? undefined : true}
        aria-label={compact ? 'Temperament Lab' : undefined}
      >
        <rect width="64" height="64" rx="16" fill="#0f6e68" />
        <g fill="none" strokeLinecap="round" transform="translate(32 32)">
          <circle
            className="logo-ring"
            r="24"
            stroke="#e8e0d4"
            strokeWidth="3.4"
            pathLength="1"
            strokeDasharray="0.78 0.22"
            transform="rotate(-18)"
            style={{ '--ring-delay': '0ms' }}
          />
          <circle
            className="logo-ring"
            r="18"
            stroke="#c46a3a"
            strokeWidth="3.4"
            pathLength="1"
            strokeDasharray="0.78 0.22"
            transform="rotate(72)"
            style={{ '--ring-delay': '90ms' }}
          />
          <circle
            className="logo-ring"
            r="12"
            stroke="#c9a15b"
            strokeWidth="3.4"
            pathLength="1"
            strokeDasharray="0.78 0.22"
            transform="rotate(162)"
            style={{ '--ring-delay': '180ms' }}
          />
          <circle
            className="logo-ring"
            r="6.5"
            stroke="#f6f3ee"
            strokeWidth="3.2"
            pathLength="1"
            strokeDasharray="0.78 0.22"
            transform="rotate(252)"
            style={{ '--ring-delay': '270ms' }}
          />
          <circle r="2.2" fill="#f6f3ee" />
        </g>
      </svg>
      {!compact && (
        <span
          className={`text-sm font-semibold tracking-[0.14em] ${inverted ? 'text-white' : 'text-teal'}`}
        >
          Temperament Lab
        </span>
      )}
    </span>
  )
}
