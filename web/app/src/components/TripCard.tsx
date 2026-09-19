import type { Trip } from '../types'

interface TripCardProps {
  trip: Trip
}

export function TripCard({ trip }: TripCardProps) {
  return (
    <article className="overflow-hidden rounded-lg border border-outline-variant/70 bg-surface-container-lowest shadow-raised">
      <div className="flex flex-col gap-5 border-b border-outline-variant/60 bg-surface-container-low px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">Active journey</p>
          <h2 className="mt-2 text-2xl font-bold tracking-tight">{trip.traveller_name}</h2>
        </div>
        <span className="w-fit rounded-full bg-primary-fixed px-3 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-primary">
          {trip.status}
        </span>
      </div>
      <div className="grid gap-6 p-6 sm:grid-cols-[1fr_auto_1fr] sm:items-center">
        <div>
          <p className="font-mono text-4xl font-semibold tracking-tight">{trip.origin}</p>
          <p className="mt-1 text-sm text-on-surface-variant">Origin</p>
        </div>
        <div className="flex items-center gap-3 text-primary" aria-label={`${trip.flights.length} flight legs`}>
          <span className="h-px w-12 bg-outline-variant" />
          <span aria-hidden="true">✈</span>
          <span className="h-px w-12 bg-outline-variant" />
        </div>
        <div className="sm:text-right">
          <p className="font-mono text-4xl font-semibold tracking-tight">{trip.destination}</p>
          <p className="mt-1 text-sm text-on-surface-variant">Destination</p>
        </div>
      </div>
    </article>
  )
}
