/**
 * Where the dashboard gets its data.
 *
 * The app stays mock-first (C1): if our API is not reachable the contract-shaped
 * mocks render the same screen, so the demo survives venue wifi. When the API
 * answers, it wins — and every refetch below is allowed to fail quietly so a
 * dropped request keeps the last known state on screen instead of blanking it.
 */
import type { AgentAction, RecoveryPlan, Trip } from '../types'
import { apiTravelService } from './api'
import { mockTravelService } from './mock'

export { apiTravelService, mockTravelService }
export { mockTravelService as travelService }

export type DataSource = 'api' | 'mock'

export interface Snapshot {
  source: DataSource
  /**
   * Every trip the source returned. Only `trip` is rendered; this is here so the
   * switcher can list the other travellers and show their live status without a
   * second fetch. The seed has three, each demonstrating a different gate path.
   */
  trips: Trip[]
  trip: Trip
  actions: AgentAction[]
  plan: RecoveryPlan | null
  disruptionId: string | null
}

/**
 * The timeline is the only place the browser learns a disruption id — detection
 * writes it into the DETECTED row's detail. Reading it back keeps the timeline a
 * dumb render of agent_actions and survives a page refresh.
 */
export function disruptionIdFrom(actions: AgentAction[]): string | null {
  for (let index = actions.length - 1; index >= 0; index -= 1) {
    const candidate = actions[index]?.detail?.disruption_id
    if (typeof candidate === 'string') return candidate
  }
  return null
}

async function planFor(disruptionId: string | null): Promise<RecoveryPlan | null> {
  if (!disruptionId) return null
  try {
    return await apiTravelService.getPlan(disruptionId)
  } catch {
    return null
  }
}

/** Timeline + plan for one trip out of an already-fetched set. Throws on a failed fetch. */
async function apiSnapshot(trips: Trip[], trip: Trip): Promise<Snapshot> {
  const actions = await apiTravelService.getTimeline(trip.id)
  const disruptionId = disruptionIdFrom(actions)
  return { source: 'api', trips, trip, actions, plan: await planFor(disruptionId), disruptionId }
}

async function mockSnapshot(): Promise<Snapshot> {
  const trips = await mockTravelService.getTrips()
  const [trip] = trips
  // Throwing here is what makes EmptyState reachable. Without it an empty mock set
  // returns `trip: undefined` and the Dashboard crashes on `trip.flights` instead.
  if (!trip) throw new Error('No trip in the mock set')
  return {
    source: 'mock',
    trips,
    trip,
    actions: await mockTravelService.getTimeline(trip.id),
    plan: await mockTravelService.getPlan(),
    disruptionId: null,
  }
}

/** First paint. Falls back to mocks if the API is unreachable or has no trips. */
export async function loadSnapshot(): Promise<Snapshot> {
  try {
    const trips = await apiTravelService.getTrips()
    const [trip] = trips
    if (!trip) throw new Error('API returned no trips')
    return await apiSnapshot(trips, trip)
  } catch {
    return mockSnapshot()
  }
}

/**
 * Put a different traveller on screen.
 *
 * Deliberately not a `loadSnapshot(tripId)`: that would fall back to mocks, so an
 * API that died mid-session would answer a switch by silently swapping the whole
 * dashboard to fixture data. Null instead — the caller keeps what it has.
 */
export async function selectTrip(trips: Trip[], tripId: string): Promise<Snapshot | null> {
  const trip = trips.find((candidate) => candidate.id === tripId)
  if (!trip) return null
  try {
    return await apiSnapshot(trips, trip)
  } catch {
    return null
  }
}

/** Refetch one surface. Resolves to null when the call fails — caller keeps state. */
export const refetch = {
  /**
   * The whole set, not one trip: a status change on an unselected traveller has to
   * reach their chip in the switcher, and this is one request either way.
   */
  trips: async (): Promise<Trip[] | null> => {
    try {
      return await apiTravelService.getTrips()
    } catch {
      return null
    }
  },
  timeline: async (tripId: string): Promise<AgentAction[] | null> => {
    try {
      return await apiTravelService.getTimeline(tripId)
    } catch {
      return null
    }
  },
  plan: planFor,
}
