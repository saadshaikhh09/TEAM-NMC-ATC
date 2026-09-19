import { useState } from 'react'
import { AgentTimeline } from '../components/AgentTimeline'
import { ApprovalModal } from '../components/ApprovalModal'
import { BookingImport } from '../components/BookingImport'
import { ConfirmationCard } from '../components/ConfirmationCard'
import { FlightAlternativesCard } from '../components/FlightAlternativesCard'
import { HotelPolicyCard } from '../components/HotelPolicyCard'
import { LiveFlightStatusCard } from '../components/LiveFlightStatusCard'
import { OperationsBar } from '../components/OperationsBar'
import { RadarPanel } from '../components/RadarPanel'
import { RejectionPanel } from '../components/RejectionPanel'
import { Reveal } from '../components/Reveal'
import { TripCard } from '../components/TripCard'
import type { SimulationKind } from '../services/api'
import type { LiveStatus } from '../services/live'
import type { AgentAction, RecoveryPlan, Trip } from '../types'

export type ConnectionState = LiveStatus | 'mock'

interface DashboardProps {
  trip: Trip
  /** The full set, for the switcher. `trip` is the one this screen renders. */
  trips: Trip[]
  actions: AgentAction[]
  plan: RecoveryPlan | null
  connection: ConnectionState
  /** False on the mock path, where every write surface says why it is unavailable. */
  live: boolean
  onApprove: () => Promise<void>
  onReject: () => Promise<void>
  onSelectTrip: (tripId: string) => void
  onSimulate: (kind: SimulationKind) => Promise<void>
  onExtract: (pastedBookingText: string) => Promise<Trip>
  timelinePaceMs?: number
}

/** Never implies live airline write access: simulated feed, real logic, sandbox booking. */
const CONNECTION_COPY: Record<ConnectionState, { label: string; detail: string }> = {
  connecting: { label: 'Connecting', detail: 'Opening the agent event stream.' },
  live: { label: 'Live', detail: 'Agent events stream in over WebSocket as the simulated feed fires.' },
  reconnecting: { label: 'Reconnecting', detail: 'Stream dropped. The last known state stays on screen.' },
  polling: { label: 'Polling', detail: 'Stream unavailable, so the dashboard polls our API instead.' },
  mock: { label: 'Mock data', detail: 'Contract-shaped mocks keep this dashboard available without the API.' },
}

export function Dashboard({
  trip,
  trips,
  actions,
  plan,
  connection,
  live,
  onApprove,
  onReject,
  onSelectTrip,
  onSimulate,
  onExtract,
  timelinePaceMs,
}: DashboardProps) {
  const [approvalOpen, setApprovalOpen] = useState(false)
  const connectionCopy = CONNECTION_COPY[connection]

  const decide = async (decision: () => Promise<void>) => {
    await decision()
    setApprovalOpen(false)
  }

  return (
    <section aria-labelledby="dashboard-title">
      <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-primary">Journey control</p>
          <h1 id="dashboard-title" className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Your trip, handled.
          </h1>
        </div>
        <div className="max-w-md sm:text-right" aria-live="polite">
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-on-surface-variant">
            {connectionCopy.label}
          </p>
          <p className="mt-1 text-sm leading-6 text-on-surface-variant">{connectionCopy.detail}</p>
        </div>
      </div>

      <div className="space-y-8">
        {/* Above the trip on purpose: the operator picks who is on stage and fires the
            disruption before anything below it has anything to react to. */}
        <Reveal>
          <OperationsBar
            live={live}
            onSelectTrip={onSelectTrip}
            onSimulate={onSimulate}
            trip={trip}
            trips={trips}
          />
        </Reveal>

        <Reveal>
          <RadarPanel flights={trip.flights} status={trip.status} />
        </Reveal>

        <Reveal>
          <TripCard trip={trip} />
        </Reveal>

        {trip.flights.length > 0 && (
          <div className="grid gap-5 lg:grid-cols-2">
            {trip.flights.map((flight, index) => (
              <Reveal delayMs={index * 90} key={flight.id}>
                <LiveFlightStatusCard flight={flight} />
              </Reveal>
            ))}
          </div>
        )}

        {plan?.state === 'EXECUTED' && (
          <Reveal>
            <ConfirmationCard actions={actions} plan={plan} />
          </Reveal>
        )}

        {plan && (
          <Reveal>
            <section
              className={`flex flex-col gap-5 rounded-lg border p-6 shadow-card sm:flex-row sm:items-center sm:justify-between ${plan.state === 'APPROVED' ? 'border-emerald-200 bg-emerald-50' : plan.state === 'REJECTED' ? 'border-red-200 bg-red-50' : 'border-primary/20 bg-primary-fixed/45'}`}
            >
              <div>
                <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">
                  Recovery plan · {plan.state}
                </p>
                <h2 className="mt-2 text-xl font-bold">
                  {plan.state === 'APPROVED'
                    ? 'Plan approved and ready to execute.'
                    : plan.state === 'REJECTED'
                      ? 'Plan rejected. No action was taken.'
                      : plan.approval_reason}
                </h2>
              </div>
              {plan.state === 'AWAITING_APPROVAL' && (
                <button
                  className="lift shrink-0 rounded-lg bg-primary px-5 py-3 font-semibold text-white shadow-card hover:bg-primary-container focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
                  onClick={() => setApprovalOpen(true)}
                  type="button"
                >
                  Review recovery plan
                </button>
              )}
            </section>
          </Reveal>
        )}

        {plan && (
          <Reveal>
            <FlightAlternativesCard constraints={trip.constraints} plan={plan} />
          </Reveal>
        )}

        {plan && (
          <Reveal>
            <RejectionPanel rejections={plan.rejections} />
          </Reveal>
        )}

        {trip.hotels.map((hotel, index) => (
          <Reveal delayMs={index * 90} key={hotel.id}>
            <HotelPolicyCard change={plan?.hotel_change} hotel={hotel} />
          </Reveal>
        ))}

        <Reveal>
          <AgentTimeline actions={actions} paceMs={timelinePaceMs} />
        </Reveal>

        {/* Last: adding a trip is the one thing on this screen that is not about the
            disruption already in progress. */}
        <Reveal>
          <BookingImport live={live} onExtract={onExtract} />
        </Reveal>
      </div>

      {approvalOpen && plan && (
        <ApprovalModal
          onApprove={() => decide(onApprove)}
          onClose={() => setApprovalOpen(false)}
          onReject={() => decide(onReject)}
          plan={plan}
        />
      )}
    </section>
  )
}
