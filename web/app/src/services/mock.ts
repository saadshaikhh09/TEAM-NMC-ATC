import { recoveryPlan } from '../mocks/plan'
import { timelineActions } from '../mocks/timeline'
import { trips } from '../mocks/trips'

export const mockTravelService = {
  getTrips: async () => trips,
  getTrip: async (id: string) => trips.find((trip) => trip.id === id) ?? null,
  getTimeline: async (tripId: string) => timelineActions.filter((action) => action.trip_id === tripId),
  getPlan: async () => recoveryPlan,
  approvePlan: async (_id: string) => ({ ...recoveryPlan, state: 'APPROVED' as const }),
  rejectPlan: async (_id: string) => ({ ...recoveryPlan, state: 'REJECTED' as const }),
}
