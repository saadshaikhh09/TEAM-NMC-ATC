import { useState } from 'react'
import { ApiError, type SimulationKind } from '../services/api'
import type { FlightStatus, Trip, TripStatus } from '../types'

interface OperationsBarProps {
  trips: Trip[]
  trip: Trip
  /** Mock data is read-only: the harness writes a real row, so it needs a real API. */
  live: boolean
  onSelectTrip: (tripId: string) => void
  /** Rejects with the API's own reason so this bar can print it. */
  onSimulate: (kind: SimulationKind) => Promise<void>
}

/**
 * Chip tone by phase, not by name: watching, working, broken. Three tones is all
 * a glanceable strip can carry, and the exact status is spelled out beside it.
 */
const OUTCOME: Record<SimulationKind, FlightStatus> = { cancellation: 'CANCELLED', delay: 'DELAYED' }

const WATCHING: ReadonlySet<TripStatus> = new Set<TripStatus>(['CREATED', 'MONITORING', 'RECOVERED'])
const BROKEN: ReadonlySet<TripStatus> = new Set<TripStatus>(['DISRUPTED', 'RECOVERY_FAILED'])

function chipClass(status: TripStatus) {
  if (BROKEN.has(status)) return 'bg-red-500/15 text-red-200'
  if (WATCHING.has(status)) return 'bg-emerald-400/15 text-emerald-200'
  return 'bg-amber-400/15 text-amber-200'
}

/**
 * The operator's side of the screen: which traveller is on stage, and the button
 * that disrupts them.
 *
 * Navy rather than a white card on purpose. Everything below this bar is the
 * traveller's own trip; this is our test harness, and the demo script requires
 * saying so out loud rather than dressing it up as a product feature. Keeping the
 * two registers visually separate is the honest version of that sentence.
 */
export function OperationsBar({ trips, trip, live, onSelectTrip, onSimulate }: OperationsBarProps) {
  const [pending, setPending] = useState<SimulationKind | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Detection targets a leg, not a trip. Outbound is the demo leg; falling back to
  // the first flight keeps this working for a one-way trip.
  const target = trip.flights.find((flight) => flight.leg === 'outbound') ?? trip.flights[0]

  const fire = async (kind: SimulationKind) => {
    if (!target) return
    // `detect()` is idempotent: given a leg that is already CANCELLED it returns the
    // existing disruption, writes no timeline row and emits no event. Firing anyway
    // would answer 200 while the screen sat still, which reads as a broken button.
    if (target.status === OUTCOME[kind]) {
      setError(
        `${target.flight_number} is already ${OUTCOME[kind].toLowerCase()}. Run \`make reset\` to rehearse it again.`,
      )
      return
    }
    setPending(kind)
    setError(null)
    try {
      await onSimulate(kind)
    } catch (cause) {
      const reason = cause instanceof Error ? cause.message : 'The simulator did not answer.'
      // A 409 means this leg has already been disrupted — the usual state between
      // rehearsals, and the fix is a command rather than another click.
      const repeated = cause instanceof ApiError && cause.status === 409
      setError(repeated ? `${reason} Run \`make reset\` to rehearse it again.` : reason)
    } finally {
      setPending(null)
    }
  }

  const disabled = !live || !target || pending !== null

  return (
    <section
      aria-labelledby="operations-heading"
      className="rounded-lg border border-white/10 bg-navy px-6 py-6 text-white shadow-raised"
    >
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-white/50">
            Test harness · declared
          </p>
          <h2 className="mt-2 text-lg font-bold tracking-tight" id="operations-heading">
            Simulated feed, real decision logic.
          </h2>
          <p className="mt-1 max-w-lg text-sm leading-6 text-white/60">
            A simulated disruption writes the same row and fires the same event as a polled one.
            Everything after this point is the agent deciding for itself.
          </p>

          {trips.length > 1 && (
            <div className="mt-5">
              <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-white/50">
                Traveller on screen
              </p>
              {/* Flight strips, the way a controller keeps one per aircraft: route in mono,
                  name, live status. The route is what tells them apart at a glance. */}
              <div className="mt-3 flex flex-wrap gap-2">
                {trips.map((candidate) => {
                  const selected = candidate.id === trip.id
                  return (
                    <button
                      aria-pressed={selected}
                      className={`lift min-w-[9.5rem] rounded-md border px-3 py-2.5 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-navy ${
                        selected
                          ? 'border-white/60 bg-white/15'
                          : 'border-white/15 bg-white/5 hover:bg-white/10'
                      }`}
                      key={candidate.id}
                      onClick={() => onSelectTrip(candidate.id)}
                      type="button"
                    >
                      <span className="block font-mono text-xs font-semibold tracking-[0.08em]">
                        {candidate.origin} <span aria-hidden="true">→</span> {candidate.destination}
                      </span>
                      <span className="mt-1 block truncate text-sm font-semibold text-white/90">
                        {candidate.traveller_name}
                      </span>
                      <span
                        className={`mt-2 inline-block rounded-full px-2 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-[0.12em] ${chipClass(candidate.status)}`}
                      >
                        {candidate.status}
                      </span>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        <div className="shrink-0 lg:max-w-xs lg:text-right">
          <div className="flex flex-wrap gap-2 lg:justify-end">
            <button
              className="lift rounded-lg bg-red-500 px-4 py-3 text-sm font-semibold text-white shadow-card hover:bg-red-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-navy disabled:cursor-not-allowed disabled:bg-white/10 disabled:text-white/40 disabled:shadow-none"
              disabled={disabled}
              onClick={() => void fire('cancellation')}
              type="button"
            >
              {pending === 'cancellation' ? 'Cancelling…' : 'Simulate a cancellation'}
            </button>
            <button
              className="lift rounded-lg border border-white/25 bg-white/10 px-4 py-3 text-sm font-semibold text-white hover:bg-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-navy disabled:cursor-not-allowed disabled:border-white/10 disabled:bg-transparent disabled:text-white/40"
              disabled={disabled}
              onClick={() => void fire('delay')}
              type="button"
            >
              {pending === 'delay' ? 'Delaying…' : 'Simulate a delay'}
            </button>
          </div>

          <p className="mt-3 text-xs leading-5 text-white/55">
            {!live
              ? 'Mock data is already showing a disrupted trip. Start the API to fire a real event.'
              : !target
                ? 'This trip has no flight to disrupt.'
                : target.status === 'SCHEDULED'
                  ? `Targets ${target.flight_number}, the ${target.leg} leg.`
                  : `${target.flight_number} is already ${target.status.toLowerCase()}. Run \`make reset\` to rehearse it again.`}
          </p>

          <p aria-live="polite" className="mt-2 min-h-5 text-xs leading-5 text-red-200">
            {error}
          </p>
        </div>
      </div>
    </section>
  )
}
