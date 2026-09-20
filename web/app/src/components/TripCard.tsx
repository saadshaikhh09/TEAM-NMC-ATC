import { formatInr, formatInrOrNone } from '../lib/format'
import { Tooltip } from './Tooltip'
import type { Trip } from '../types'

interface TripCardProps {
  trip: Trip
}

/**
 * Who is travelling and the rules the agent must obey.
 *
 * The legs themselves belong to LiveFlightStatusCard and the hotel to
 * HotelPolicyCard — each of those carries live state this card has no business
 * duplicating.
 */
export function TripCard({ trip }: TripCardProps) {
  const constraints = trip.constraints

  return (
    <article className="overflow-hidden rounded-lg border border-outline-variant/70 bg-surface-container-lowest shadow-raised">
      <div className="flex flex-col gap-5 border-b border-outline-variant/60 bg-surface-container-low px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">Active journey</p>
          <h2 className="mt-2 text-2xl font-bold tracking-tight">{trip.traveller_name}</h2>
          <p className="mt-1 font-mono text-sm text-on-surface-variant">
            {trip.origin} <span aria-hidden="true">→</span> {trip.destination}
          </p>
        </div>
        <span className="w-fit rounded-full bg-primary-fixed px-3 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-primary">
          {trip.status}
        </span>
      </div>

      <section className="border-b border-outline-variant/60 bg-primary-fixed/45 px-6 py-6" aria-labelledby="constraints-heading">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-xl">
            <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-primary">Traveller safeguard</p>
            <h3 id="constraints-heading" className="mt-2 text-xl font-bold">
              {constraints.hard_arrival_by_local ? `Arrive by ${constraints.hard_arrival_by_local}` : 'No hard arrival deadline'}
            </h3>
            <p className="mt-2 text-sm leading-6 text-on-surface-variant">{constraints.hard_arrival_reason}</p>
          </div>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4 lg:min-w-[34rem]">
            <div>
              <dt className="text-xs text-on-surface-variant">Fare cap</dt>
              <dd className="mt-1 font-semibold">{formatInrOrNone(constraints.max_fare_inr)}</dd>
            </div>
            <div>
              <dt className="text-xs text-on-surface-variant">Max stops</dt>
              <dd className="mt-1 font-semibold">{constraints.max_stops ?? 'Not set'}</dd>
            </div>
            <div>
              <dt className="text-xs text-on-surface-variant">Cabin</dt>
              <dd className="mt-1 capitalize font-semibold">{constraints.cabin ?? 'Not set'}</dd>
            </div>
            <div>
              <dt className="text-xs text-on-surface-variant">
                <Tooltip label="Below this fare the agent rebooks on its own. At or above it, the plan waits for you.">
                  <span>Auto-approve</span>
                </Tooltip>
              </dt>
              <dd className="mt-1 font-semibold">{constraints.auto_approve_under_inr === null ? 'Not set' : formatInr(constraints.auto_approve_under_inr)}</dd>
            </div>
          </dl>
        </div>
        <p className="mt-4 text-xs text-on-surface-variant">
          Avoided carriers: {constraints.avoid_carriers?.length ? constraints.avoid_carriers.join(', ') : 'None'}
        </p>
      </section>
    </article>
  )
}
