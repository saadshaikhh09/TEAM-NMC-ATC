import { formatInr } from '../lib/format'
import type { Flight, Trip } from '../types'

interface TripCardProps {
  trip: Trip
}

function FlightLeg({ flight }: { flight: Flight }) {
  return (
    <section className="rounded-md border border-outline-variant/60 bg-white p-5" aria-label={`${flight.leg} flight`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-on-surface-variant">
            {flight.leg} leg
          </p>
          <h3 className="mt-1 text-lg font-bold">{flight.flight_number}</h3>
        </div>
        <span className="rounded-full bg-emerald-50 px-2.5 py-1 font-mono text-[10px] font-semibold text-emerald-700">
          {flight.status}
        </span>
      </div>

      <div className="mt-5 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
        <div>
          <p className="font-mono text-2xl font-semibold">{flight.origin}</p>
          <p className="mt-1 text-sm font-semibold">{flight.departure_local}</p>
        </div>
        <div className="flex items-center gap-2 text-primary" aria-hidden="true">
          <span className="h-px w-5 bg-outline-variant sm:w-10" />
          <span>✈</span>
          <span className="h-px w-5 bg-outline-variant sm:w-10" />
        </div>
        <div className="text-right">
          <p className="font-mono text-2xl font-semibold">{flight.destination}</p>
          <p className="mt-1 text-sm font-semibold">{flight.arrival_local}</p>
        </div>
      </div>
    </section>
  )
}

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
              Arrive by {constraints.hard_arrival_by_local}
            </h3>
            <p className="mt-2 text-sm leading-6 text-on-surface-variant">{constraints.hard_arrival_reason}</p>
          </div>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4 lg:min-w-[34rem]">
            <div>
              <dt className="text-xs text-on-surface-variant">Fare cap</dt>
              <dd className="mt-1 font-semibold">{formatInr(constraints.max_fare_inr)}</dd>
            </div>
            <div>
              <dt className="text-xs text-on-surface-variant">Max stops</dt>
              <dd className="mt-1 font-semibold">{constraints.max_stops}</dd>
            </div>
            <div>
              <dt className="text-xs text-on-surface-variant">Cabin</dt>
              <dd className="mt-1 capitalize font-semibold">{constraints.cabin}</dd>
            </div>
            <div>
              <dt className="text-xs text-on-surface-variant">Auto-approve</dt>
              <dd className="mt-1 font-semibold">{formatInr(constraints.auto_approve_under_inr)}</dd>
            </div>
          </dl>
        </div>
        <p className="mt-4 text-xs text-on-surface-variant">
          Avoided carriers: {constraints.avoid_carriers.length ? constraints.avoid_carriers.join(', ') : 'None'}
        </p>
      </section>

      <div className="grid gap-5 p-6 lg:grid-cols-2">
        {trip.flights.map((flight) => (
          <FlightLeg flight={flight} key={flight.id} />
        ))}
      </div>

      {trip.hotels.map((hotel) => (
        <section className="mx-6 mb-6 rounded-md border border-outline-variant/60 bg-surface-container-low p-5" key={hotel.id}>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-on-surface-variant">
                Hotel · {hotel.status}
              </p>
              <h3 className="mt-1 text-lg font-bold">{hotel.name}</h3>
              <p className="mt-1 text-sm text-on-surface-variant">
                {hotel.city} · Confirmation {hotel.confirmation_number}
              </p>
            </div>
            <dl className="grid grid-cols-3 gap-5 text-sm">
              <div>
                <dt className="text-xs text-on-surface-variant">Check-in</dt>
                <dd className="mt-1 font-semibold">{hotel.check_in}</dd>
              </div>
              <div>
                <dt className="text-xs text-on-surface-variant">Check-out</dt>
                <dd className="mt-1 font-semibold">{hotel.check_out}</dd>
              </div>
              <div>
                <dt className="text-xs text-on-surface-variant">Nightly</dt>
                <dd className="mt-1 font-semibold">{formatInr(hotel.nightly_rate_inr)}</dd>
              </div>
            </dl>
          </div>
        </section>
      ))}
    </article>
  )
}
