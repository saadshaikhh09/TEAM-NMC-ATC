import { AgentTimeline } from '../components/AgentTimeline'
import { TripCard } from '../components/TripCard'
import type { AgentAction, Trip } from '../types'

interface DashboardProps {
  trip: Trip
  actions: AgentAction[]
  timelinePaceMs?: number
}

export function Dashboard({ trip, actions, timelinePaceMs }: DashboardProps) {
  return (
    <section aria-labelledby="dashboard-title">
      <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-primary">Journey control</p>
          <h1 id="dashboard-title" className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Your trip, handled.
          </h1>
        </div>
        <p className="max-w-md text-sm leading-6 text-on-surface-variant">
          Contract-shaped mock data keeps this dashboard available without the API or network.
        </p>
      </div>
      <div className="space-y-8">
        <TripCard trip={trip} />
        <AgentTimeline actions={actions} paceMs={timelinePaceMs} />
      </div>
    </section>
  )
}
