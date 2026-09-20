import { lazy, Suspense } from 'react'
import { formatDelta, formatInrOrNone } from '../lib/format'
import { Tooltip } from './Tooltip'
import type { Hotel, HotelChange } from '../types'

const HotelMap = lazy(() => import('./HotelMap').then((module) => ({ default: module.HotelMap })))

interface HotelPolicyCardProps {
  hotel: Hotel
  /**
   * Present once a recovery plan exists and has worked out the knock-on hotel
   * move. Null when the plan exists but has no hotel to move — the API sends
   * `hotel_change: null` for a trip with no hotel row, or a plan with no chosen
   * option to price the move against.
   */
  change?: HotelChange | null
}

/**
 * The hotel leg and what the recovery plan does to it.
 *
 * Our hotel provider has no modify endpoint, so a date shift is a cancel followed by
 * a rebook. That is a materially riskier operation than editing a booking, and the
 * card says so rather than hiding it behind the word "updated".
 */
export function HotelPolicyCard({ hotel, change }: HotelPolicyCardProps) {
  const moving = change?.required === true

  return (
    <article
      aria-labelledby={`hotel-${hotel.id}`}
      className="lift overflow-hidden rounded-lg border border-outline-variant/70 bg-surface-container-lowest shadow-card hover:border-primary/30"
    >
      <div className="flex flex-col gap-6 p-6 lg:flex-row">
        <Suspense fallback={<div aria-label="Loading hotel map" className="hotel-map animate-pulse bg-surface-container-high" />}>
          <HotelMap hotel={hotel} />
        </Suspense>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-primary">
                Hotel leg · {hotel.provider}
              </p>
              <h3 className="mt-2 text-xl font-bold tracking-tight" id={`hotel-${hotel.id}`}>
                {hotel.name}
              </h3>
              <p className="mt-1 font-mono text-xs text-on-surface-variant">
                {hotel.confirmation_number
                  ? `Confirmation ${hotel.confirmation_number}`
                  : 'Confirmation pending'}
              </p>
              {hotel.address && <p className="mt-2 text-sm text-on-surface-variant">{hotel.address}</p>}
            </div>
            <span
              className={`rounded-full px-3 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] ${
                hotel.modifiable ? 'bg-emerald-50 text-emerald-700' : 'bg-orange-100 text-orange-700'
              }`}
            >
              {hotel.modifiable ? 'Flexible rate' : 'Non-flexible'}
            </span>
          </div>

          <dl className="mt-6 grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4">
            <div>
              <dt className="text-xs text-on-surface-variant">Check-in</dt>
              <dd className={`mt-1 font-semibold ${moving ? 'text-on-surface-variant line-through' : ''}`}>
                {hotel.check_in}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-on-surface-variant">Check-out</dt>
              <dd className="mt-1 font-semibold">{hotel.check_out}</dd>
            </div>
            <div>
              <dt className="text-xs text-on-surface-variant">Nightly</dt>
              <dd className="mt-1 font-semibold">
                {formatInrOrNone(hotel.nightly_rate_inr, '—')}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-on-surface-variant">Status</dt>
              <dd className="mt-1 font-semibold">{hotel.status}</dd>
            </div>
          </dl>
        </div>
      </div>

      {moving && change && (
        <div className="border-t border-outline-variant/60 bg-primary-fixed/45 px-6 py-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-primary">
                Knock-on change
              </p>
              <h4 className="mt-2 text-base font-bold">
                Check-in moves to {change.new_check_in}
              </h4>
              <p className="mt-2 max-w-xl text-sm leading-6 text-on-surface-variant">
                <Tooltip label="Our hotel provider has no modify endpoint. The agent cancels the existing booking and immediately rebooks the new dates — the room is briefly released.">
                  <span>Cancel, then rebook</span>
                </Tooltip>{' '}
                — the later flight lands after the original check-in window.
              </p>
            </div>
            <div className="shrink-0 sm:text-right">
              <p className="text-xs text-on-surface-variant">Cost impact</p>
              <p
                className={`mt-1 text-xl font-bold ${change.cost_delta_inr <= 0 ? 'text-emerald-700' : 'text-on-surface'}`}
              >
                {formatDelta(change.cost_delta_inr)}
              </p>
            </div>
          </div>
        </div>
      )}
    </article>
  )
}
