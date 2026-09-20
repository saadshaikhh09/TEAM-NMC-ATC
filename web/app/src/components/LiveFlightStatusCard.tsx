import { useEffect, useState } from 'react'
import { formatDuration, formatUtc } from '../lib/format'
import { Tooltip } from './Tooltip'
import type { Flight, FlightStatus } from '../types'

interface LiveFlightStatusCardProps {
  flight: Flight
}

/** Matches the status chip palette in the Aero Concierge design system. */
const STATUS_STYLE: Record<FlightStatus, { chip: string; dot: string; note: string }> = {
  SCHEDULED: { chip: 'bg-emerald-50 text-emerald-700', dot: 'bg-emerald-500', note: 'On schedule.' },
  DEPARTED: { chip: 'bg-emerald-50 text-emerald-700', dot: 'bg-emerald-500', note: 'In the air.' },
  LANDED: { chip: 'bg-emerald-50 text-emerald-700', dot: 'bg-emerald-500', note: 'Arrived.' },
  DELAYED: { chip: 'bg-orange-100 text-orange-700', dot: 'bg-warning', note: 'Running late. The agent is watching the gap.' },
  CANCELLED: { chip: 'bg-red-100 text-red-700', dot: 'bg-error', note: 'Cancelled. Recovery has taken over.' },
}

/** Fallback for a status the contract does not know. Prevents an unmapped value white-screening the dashboard. */
const UNKNOWN_STATUS = { chip: 'bg-surface-container text-on-surface-variant', dot: 'bg-outline', note: 'Status unrecognised.' }

/** Seconds until `iso`, floored at zero. */
function secondsUntil(iso: string, now: number) {
  const remaining = Math.round((Date.parse(iso) - now) / 1000)
  return Number.isFinite(remaining) && remaining > 0 ? remaining : 0
}

function countdownLabel(seconds: number) {
  if (seconds === 0) return 'due now'
  if (seconds < 60) return `in ${seconds}s`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `in ${minutes}m ${String(seconds % 60).padStart(2, '0')}s`
  return `in ${Math.floor(minutes / 60)}h ${String(minutes % 60).padStart(2, '0')}m`
}

/**
 * One flight leg as the monitor sees it: status, route, and when the next poll fires.
 *
 * The countdown is the honest part of this card — it shows the agent is on a tiered
 * schedule against a 500-call monthly budget, not streaming a live radar feed.
 */
export function LiveFlightStatusCard({ flight }: LiveFlightStatusCardProps) {
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(timer)
  }, [])

  const style = STATUS_STYLE[flight.status] ?? UNKNOWN_STATUS
  // The monitor nulls next_poll_at the moment it detects a disruption, so the
  // cancelled leg — the one the demo is built around — has no next poll at all.
  const nextPollAt = flight.next_poll_at
  const nextPoll = nextPollAt === null ? null : secondsUntil(nextPollAt, now)
  const grounded = flight.status === 'CANCELLED'

  // Progress along the leg, 0–1. Only meaningful once the flight is actually moving.
  const start = Date.parse(flight.scheduled_departure)
  const end = Date.parse(flight.scheduled_arrival)
  const flown =
    flight.status === 'LANDED'
      ? 1
      : flight.status === 'DEPARTED' && end > start
        ? Math.min(1, Math.max(0, (now - start) / (end - start)))
        : 0

  return (
    <article
      aria-labelledby={`status-${flight.id}`}
      className="lift rounded-lg border border-outline-variant/70 bg-surface-container-lowest p-6 shadow-card hover:border-primary/30"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-on-surface-variant">
            {flight.leg} leg · {flight.carrier}
          </p>
          <h3 className="mt-1 font-mono text-xl font-semibold tracking-[0.06em]" id={`status-${flight.id}`}>
            {flight.flight_number}
          </h3>
        </div>
        <span
          className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] ${style.chip}`}
        >
          <span className="relative flex size-2">
            {!grounded && (
              <span className={`ping-ring absolute inline-flex size-2 rounded-full ${style.dot} opacity-75`} />
            )}
            <span className={`relative inline-flex size-2 rounded-full ${style.dot}`} />
          </span>
          {flight.status}
        </span>
      </div>

      <div className="mt-6 grid grid-cols-[1fr_auto_1fr] items-end gap-4">
        <div>
          <p className="font-mono text-3xl font-semibold leading-none">{flight.origin}</p>
          <p className="mt-2 text-sm font-semibold">{flight.departure_local}</p>
        </div>
        <div className="pb-1 text-center text-primary" aria-hidden="true">
          <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-on-surface-variant">
            {formatDuration(flight.scheduled_departure, flight.scheduled_arrival)}
          </span>
        </div>
        <div className="text-right">
          <p className="font-mono text-3xl font-semibold leading-none">{flight.destination}</p>
          <p className="mt-2 text-sm font-semibold">{flight.arrival_local}</p>
        </div>
      </div>

      <div
        aria-hidden="true"
        className="relative mt-5 h-1.5 overflow-hidden rounded-full bg-surface-container-high"
      >
        <div
          className={`h-full rounded-full transition-[width] duration-1000 ease-linear ${grounded ? 'bg-error' : 'bg-primary'}`}
          style={{ width: grounded ? '100%' : `${Math.round(flown * 100)}%` }}
        />
      </div>

      <div className="mt-5 flex flex-col gap-2 border-t border-outline-variant/50 pt-4 text-sm text-on-surface-variant sm:flex-row sm:items-center sm:justify-between">
        <p>{style.note}</p>
        <p className="font-mono text-[10px] uppercase tracking-[0.12em]">
          {nextPollAt === null || nextPoll === null ? (
            flight.booking_reference?.startsWith('MOCK-') ? <span>Mock booking {flight.booking_reference}</span> :
              <Tooltip label="This leg is disrupted or finished, so the monitor has stopped scheduling polls for it. Recovery drives what happens next.">
                <span>Polling stopped</span>
              </Tooltip>
          ) : (
            <Tooltip
              label={`The monitor polls on a tiered schedule to stay inside a 500-call monthly budget. Scheduled for ${formatUtc(nextPollAt)}.`}
            >
              <span>Next check {countdownLabel(nextPoll)}</span>
            </Tooltip>
          )}
        </p>
      </div>
    </article>
  )
}
