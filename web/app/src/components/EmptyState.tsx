interface EmptyStateProps {
  onRetry?: () => void
}

/** Reuses the disrupted-flight-path artwork from the 404 design for an empty account. */
export function EmptyState({ onRetry }: EmptyStateProps) {
  return (
    <section
      aria-labelledby="empty-heading"
      className="rounded-lg border border-outline-variant/70 bg-surface-container-lowest px-6 py-16 text-center shadow-card"
    >
      <svg
        aria-hidden="true"
        className="mx-auto h-24 w-full max-w-sm"
        fill="none"
        viewBox="0 0 320 96"
      >
        {/* The intended route, then the break. */}
        <path d="M12 72 Q 90 20 150 44" stroke="#0050cb" strokeLinecap="round" strokeWidth="2.5" />
        <path
          d="M170 50 Q 240 74 308 26"
          stroke="#c2c6d8"
          strokeDasharray="6 8"
          strokeLinecap="round"
          strokeWidth="2.5"
        />
        <circle cx="12" cy="72" fill="#0050cb" r="4" />
        <circle cx="308" cy="26" fill="none" r="4" stroke="#727687" strokeWidth="2" />
        <g stroke="#ba1a1a" strokeLinecap="round" strokeWidth="2.5">
          <line x1="152" x2="172" y1="34" y2="58" />
          <line x1="172" x2="152" y1="34" y2="58" />
        </g>
      </svg>

      <p className="mt-8 font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-on-surface-variant">
        No trip on screen
      </p>
      <h2 className="mt-3 text-2xl font-bold tracking-tight" id="empty-heading">
        The concierge has nothing to watch.
      </h2>
      <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-on-surface-variant">
        Add an itinerary to begin monitoring. Nothing has been lost and no booking is changed by
        this screen.
      </p>

      {onRetry && (
        <button
          className="lift mt-8 rounded-lg bg-primary px-5 py-3 font-semibold text-white shadow-card hover:bg-primary-container focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
          onClick={onRetry}
          type="button"
        >
          Try again
        </button>
      )}
    </section>
  )
}
