import { useCallback, useEffect, useRef, useState } from 'react'
import { AppShell } from './components/AppShell'
import { EmptyState } from './components/EmptyState'
import { FlightAlternativesSkeleton, FlightStatusSkeleton, HotelPolicySkeleton } from './components/Skeletons'
import { Dashboard } from './screens/Dashboard'
import {
  apiTravelService,
  disruptionIdFrom,
  loadSnapshot,
  mockTravelService,
  refetch,
  selectTrip,
  type Snapshot,
} from './services'
import type { SimulationKind } from './services/api'
import { connectLive, type LiveStatus } from './services/live'
import type { WsEvent } from './types'

function App() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const [status, setStatus] = useState<LiveStatus>('connecting')
  // Both the API and the mocks failed. Without this the skeleton would spin forever.
  const [unavailable, setUnavailable] = useState(false)
  // Event callbacks read the latest snapshot through a ref so the subscription
  // is opened once and never torn down by an unrelated state change.
  const snapshotRef = useRef<Snapshot | null>(null)

  const apply = useCallback((next: Snapshot) => {
    snapshotRef.current = next
    setSnapshot(next)
  }, [])

  // The flag clears only once a retry actually succeeds — clearing it up front would
  // flash the skeleton over an empty state that is about to come back anyway.
  const load = useCallback(() => {
    void loadSnapshot()
      .then((next) => {
        apply(next)
        setUnavailable(false)
      })
      .catch(() => setUnavailable(true))
  }, [apply])

  useEffect(load, [load])

  /**
   * Refetches the whole trip set, then re-reads the selected trip out of it.
   *
   * One request keeps both the dashboard and the switcher's status chips current,
   * so a traveller who is not on screen still visibly moves when their flight goes.
   */
  const refreshTrips = useCallback(async () => {
    const current = snapshotRef.current
    if (current?.source !== 'api') return
    const trips = await refetch.trips()
    const latest = snapshotRef.current
    if (!trips || !latest) return
    const trip = trips.find((candidate) => candidate.id === latest.trip.id)
    apply({ ...latest, trips, trip: trip ?? latest.trip })
  }, [apply])

  const refreshTimeline = useCallback(async () => {
    const current = snapshotRef.current
    if (current?.source !== 'api') return
    const actions = await refetch.timeline(current.trip.id)
    const latest = snapshotRef.current
    if (!actions || !latest) return
    apply({ ...latest, actions, disruptionId: disruptionIdFrom(actions) ?? latest.disruptionId })
  }, [apply])

  const refreshPlan = useCallback(async (disruptionId?: string) => {
    const current = snapshotRef.current
    if (current?.source !== 'api') return
    const id = disruptionId ?? current.disruptionId
    if (!id) return
    const plan = await refetch.plan(id)
    const latest = snapshotRef.current
    // A failed fetch keeps the last known plan rather than emptying the panel.
    if (latest) apply({ ...latest, disruptionId: id, plan: plan ?? latest.plan })
  }, [apply])

  /**
   * The eight names in CONTRACT.md are fixed strings and this switch is the only
   * place they are interpreted. Anything else is dropped silently.
   */
  const handleEvent = useCallback(
    (event: WsEvent) => {
      const current = snapshotRef.current
      if (current?.source !== 'api') return

      // An event for a trip that is not on screen still has to move that traveller's
      // chip in the switcher. It must not touch the timeline or plan being shown.
      if (event.trip_id !== current.trip.id) {
        if (event.type === 'trip.updated' || event.type === 'disruption.detected') void refreshTrips()
        return
      }

      switch (event.type) {
        case 'trip.updated':
          void refreshTrips()
          break
        case 'disruption.detected': {
          const disruptionId =
            typeof event.payload.disruption_id === 'string' ? event.payload.disruption_id : undefined
          void refreshTrips()
          void refreshTimeline()
          void refreshPlan(disruptionId)
          break
        }
        case 'plan.ready':
        case 'plan.awaiting_approval':
        case 'plan.executing':
          void refreshPlan()
          break
        case 'plan.executed':
        case 'plan.failed':
          void refreshPlan()
          void refreshTrips()
          break
        case 'action.recorded':
          // The timeline stays a dumb render of agent_actions: refetch the table,
          // never assemble a row from the payload.
          void refreshTimeline()
          break
        default:
          break
      }
    },
    [refreshPlan, refreshTimeline, refreshTrips],
  )

  const poll = useCallback(() => {
    void refreshTrips()
    void refreshTimeline()
    void refreshPlan()
  }, [refreshPlan, refreshTimeline, refreshTrips])

  const isLiveSource = snapshot?.source === 'api'
  useEffect(() => {
    if (!isLiveSource) return
    return connectLive({ onEvent: handleEvent, onStatus: setStatus, onPoll: poll })
  }, [isLiveSource, handleEvent, poll])

  const decide = async (decision: 'approve' | 'reject') => {
    const current = snapshotRef.current
    if (!current?.plan) return
    const service = current.source === 'api' ? apiTravelService : mockTravelService
    try {
      const plan =
        decision === 'approve'
          ? await service.approvePlan(current.plan.id)
          : await service.rejectPlan(current.plan.id)
      const latest = snapshotRef.current
      if (latest) apply({ ...latest, plan })
    } catch {
      // The next event or poll carries the real outcome; keep what is on screen.
    }
  }

  const switchTrip = async (tripId: string) => {
    const current = snapshotRef.current
    if (current?.source !== 'api' || current.trip.id === tripId) return
    const next = await selectTrip(current.trips, tripId)
    // Null means the timeline fetch failed. Staying put beats half-swapping the screen.
    if (next) apply(next)
  }

  /**
   * Fires the declared test harness. Deliberately does not apply the response:
   * detection broadcasts `disruption.detected`, and the browser has to learn about
   * a disruption the same way whether it was simulated or polled. Errors are
   * rethrown so the bar can show the API's own reason.
   */
  const simulate = async (kind: SimulationKind) => {
    const current = snapshotRef.current
    if (current?.source !== 'api') return
    const target = current.trip.flights.find((flight) => flight.leg === 'outbound') ?? current.trip.flights[0]
    await apiTravelService.simulate(kind, target?.id)
  }

  return (
    <AppShell trip={snapshot?.trip}>
      {snapshot ? (
        <Dashboard
          actions={snapshot.actions}
          connection={snapshot.source === 'api' ? status : 'mock'}
          live={snapshot.source === 'api'}
          onApprove={() => decide('approve')}
          onExtract={apiTravelService.extractTrip}
          onReject={() => decide('reject')}
          onSelectTrip={(tripId) => void switchTrip(tripId)}
          onSimulate={simulate}
          plan={snapshot.plan}
          timelinePaceMs={850}
          trip={snapshot.trip}
          trips={snapshot.trips}
        />
      ) : unavailable ? (
        <EmptyState onRetry={load} />
      ) : (
        // Skeletons mirror the real cards so the layout does not jump on arrival.
        <div className="space-y-8">
          <FlightStatusSkeleton />
          <FlightAlternativesSkeleton />
          <HotelPolicySkeleton />
        </div>
      )}
    </AppShell>
  )
}

export default App
