import type { ReactNode } from 'react'

/**
 * Loading placeholders for the three cards that wait on a network call.
 *
 * Each one mirrors the real card's geometry so the layout does not jump when the
 * data lands. `aria-busy` plus one label per skeleton means a screen reader
 * announces "loading" once, instead of reading out a wall of empty boxes.
 */

function Bar({ className = '' }: { className?: string }) {
  return <div aria-hidden="true" className={`max-w-full animate-pulse rounded bg-surface-container-high ${className}`} />
}

function Frame({ children, label }: { children: ReactNode; label: string }) {
  return (
    <section
      aria-busy="true"
      aria-label={label}
      className="min-w-0 rounded-lg border border-outline-variant/70 bg-surface-container-lowest p-4 shadow-card sm:p-6"
    >
      {children}
    </section>
  )
}

/** Mirrors LiveFlightStatusCard. */
export function FlightStatusSkeleton() {
  return (
    <Frame label="Loading flight status">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <Bar className="h-3 w-24" />
          <Bar className="mt-3 h-6 w-40" />
        </div>
        <Bar className="h-6 w-24 rounded-full" />
      </div>
      <div className="mt-6 grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-2 sm:gap-4">
        <div className="min-w-0">
          <Bar className="h-8 w-20" />
          <Bar className="mt-2 h-4 w-28" />
        </div>
        <Bar className="h-px w-16" />
        <div className="flex min-w-0 flex-col items-end">
          <Bar className="h-8 w-20" />
          <Bar className="mt-2 h-4 w-28" />
        </div>
      </div>
      <Bar className="mt-6 h-2 w-full rounded-full" />
    </Frame>
  )
}

/** Mirrors FlightAlternativesCard: a header plus three option rows. */
export function FlightAlternativesSkeleton() {
  return (
    <Frame label="Loading flight alternatives">
      <Bar className="h-3 w-32" />
      <Bar className="mt-3 h-6 w-56" />
      <div className="mt-6 space-y-3">
        {[0, 1, 2].map((row) => (
          <div className="rounded-md border border-outline-variant/50 p-4" key={row}>
            <div className="flex items-center justify-between gap-4">
              <div className="min-w-0 flex-1">
                <Bar className="h-4 w-28" />
                <Bar className="mt-2 h-3 w-44" />
              </div>
              <Bar className="h-6 w-20" />
            </div>
          </div>
        ))}
      </div>
    </Frame>
  )
}

/** Mirrors HotelPolicyCard. */
export function HotelPolicySkeleton() {
  return (
    <Frame label="Loading hotel policy">
      <div className="flex flex-col gap-6 lg:flex-row">
        <Bar className="h-40 w-full rounded-md lg:w-64" />
        <div className="min-w-0 flex-1">
          <Bar className="h-3 w-24" />
          <Bar className="mt-3 h-6 w-48" />
          <Bar className="mt-4 h-4 w-full" />
          <Bar className="mt-2 h-4 w-3/4" />
          <div className="mt-6 grid grid-cols-3 gap-2 sm:gap-4">
            {[0, 1, 2].map((cell) => (
              <div key={cell}>
                <Bar className="h-3 w-16" />
                <Bar className="mt-2 h-5 w-20" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </Frame>
  )
}
