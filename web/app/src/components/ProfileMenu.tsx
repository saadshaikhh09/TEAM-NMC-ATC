import { useEffect, useRef, useState } from 'react'
import { formatInr, formatInrOrNone } from '../lib/format'
import type { Constraints } from '../types'

interface ProfileMenuProps {
  travellerName: string
  constraints: Constraints
}

/** "Priya Sharma" → "PS". Falls back to one letter for a single-word name. */
function initials(name: string) {
  const parts = name.trim().split(/\s+/)
  const first = parts[0]?.[0] ?? '?'
  const last = parts.length > 1 ? parts[parts.length - 1][0] : ''
  return (first + last).toUpperCase()
}

/**
 * Traveller identity and the rules the agent is bound by, in the header.
 *
 * The constraints live here rather than only on the trip card because they are the
 * answer to "why did it choose that?" — worth reaching from any scroll position.
 */
export function ProfileMenu({ travellerName, constraints }: ProfileMenuProps) {
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return

    const onPointerDown = (event: MouseEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) setOpen(false)
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false)
    }

    document.addEventListener('mousedown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('mousedown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open])

  return (
    <div className="relative" ref={containerRef}>
      <button
        aria-expanded={open}
        aria-haspopup="true"
        className="flex items-center gap-2 rounded-full border border-white/15 bg-white/10 py-1.5 pl-1.5 pr-3 text-left transition-colors hover:bg-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-navy"
        onClick={() => setOpen((previous) => !previous)}
        type="button"
      >
        <span className="grid size-7 place-items-center rounded-full bg-sky font-mono text-[10px] font-semibold text-white">
          {initials(travellerName)}
        </span>
        <span className="hidden text-xs font-semibold text-white sm:block">{travellerName}</span>
        <span aria-hidden="true" className={`text-[10px] text-white/60 transition-transform ${open ? 'rotate-180' : ''}`}>
          ▾
        </span>
      </button>

      {open && (
        <div
          className="absolute right-0 z-30 mt-2 w-72 overflow-hidden rounded-md border border-outline-variant/70 bg-surface-container-lowest text-on-surface shadow-raised"
          role="menu"
        >
          <div className="border-b border-outline-variant/60 bg-surface-container-low px-4 py-3">
            <p className="text-sm font-bold">{travellerName}</p>
            <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.12em] text-on-surface-variant">
              Traveller safeguards
            </p>
          </div>

          <dl className="divide-y divide-outline-variant/50 text-sm">
            <div className="flex items-center justify-between gap-4 px-4 py-2.5">
              <dt className="text-on-surface-variant">Arrive by</dt>
              <dd className="font-semibold">{constraints.hard_arrival_by_local ?? 'Not set'}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 px-4 py-2.5">
              <dt className="text-on-surface-variant">Fare cap</dt>
              <dd className="font-semibold">{formatInrOrNone(constraints.max_fare_inr)}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 px-4 py-2.5">
              <dt className="text-on-surface-variant">Auto-approve under</dt>
              <dd className="font-semibold">{formatInr(constraints.auto_approve_under_inr)}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 px-4 py-2.5">
              <dt className="text-on-surface-variant">Max stops</dt>
              <dd className="font-semibold">{constraints.max_stops}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 px-4 py-2.5">
              <dt className="text-on-surface-variant">Cabin</dt>
              <dd className="font-semibold capitalize">{constraints.cabin}</dd>
            </div>
          </dl>

          <p className="border-t border-outline-variant/60 bg-surface-container-low px-4 py-3 text-xs leading-5 text-on-surface-variant">
            {constraints.hard_arrival_reason}
          </p>
        </div>
      )}
    </div>
  )
}
