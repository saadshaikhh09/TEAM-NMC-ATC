/**
 * REST client for our own FastAPI. CONTRACT.md is the only source of shapes.
 *
 * Nothing here ever calls a status provider or a model API directly — the
 * browser talks to our API and to nothing else.
 */
import type { AgentAction, Disruption, RecoveryPlan, Trip } from '../types'

/** Empty in dev: vite proxies /trips, /approvals, /disruptions, /simulate and /ws to :8000. */
export const apiBase = import.meta.env.VITE_API_URL ?? ''
export const AUTH_EXPIRED_EVENT = 'atc:auth-expired'

/**
 * Carries the API's own `detail` string, not just the status code.
 *
 * Read calls swallow failures and keep the last known state, so they never need
 * this. Write calls do: a 409 from /simulate and a 503 from /trips/extract both
 * have a cause the traveller can act on, and dropping it leaves the button
 * looking broken instead of answered.
 */
export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/** FastAPI puts the human-readable cause in `detail`. */
async function reasonFor(response: Response, path: string): Promise<string> {
  try {
    const body: unknown = await response.json()
    const detail = (body as { detail?: unknown }).detail
    if (typeof detail === 'string' && detail) return detail
  } catch {
    // Not JSON — a proxy error page or an empty body. The status line still says something.
  }
  return `${path} -> ${response.status}`
}

export async function send<T>(path: string, method: 'GET' | 'POST', body?: unknown): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    method,
    credentials: 'include',
    ...(body === undefined
      ? {}
      : { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  })
  if (!response.ok) {
    if (response.status === 401 && path !== '/auth/session') window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT))
    throw new ApiError(await reasonFor(response, path), response.status)
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

export interface Account {
  id: string
  name: string
  email: string
}

export const authApi = {
  session: () => send<Account>('/auth/session', 'GET'),
  login: (email: string, password: string) => send<Account>('/auth/login', 'POST', { email, password }),
  register: (name: string, email: string, password: string) =>
    send<Account>('/auth/register', 'POST', { name, email, password }),
  logout: () => send<void>('/auth/logout', 'POST'),
}

/** The two disruption kinds routes/simulate.py exposes. */
export type SimulationKind = 'cancellation' | 'delay'

export const apiTravelService = {
  getTrips: () => send<Trip[]>('/trips', 'GET'),
  getTrip: (tripId: string) => send<Trip>(`/trips/${tripId}`, 'GET'),
  getTimeline: (tripId: string) => send<AgentAction[]>(`/trips/${tripId}/timeline`, 'GET'),
  getPlan: (disruptionId: string) => send<RecoveryPlan>(`/disruptions/${disruptionId}/plan`, 'GET'),
  createTrip: (payload: unknown) => send<Trip>('/trips', 'POST', payload),
  approvePlan: (planId: string) => send<RecoveryPlan>(`/approvals/${planId}/approve`, 'POST'),
  rejectPlan: (planId: string) => send<RecoveryPlan>(`/approvals/${planId}/reject`, 'POST'),

  /**
   * The declared test harness. Writes the same `disruptions` row and fires the
   * same event as a real detection, so the browser learns about it exactly the
   * way it learns about a polled one — over /ws, never from this response.
   *
   * `flight_id` is a query parameter server-side. Omitting it targets the seeded
   * demo trip's outbound leg, which is only ever what we want when the caller
   * has no flight to name.
   */
  simulate: (kind: SimulationKind, flightId?: string) =>
    send<Disruption>(
      `/simulate/${kind}${flightId ? `?flight_id=${encodeURIComponent(flightId)}` : ''}`,
      'POST',
    ),

  /**
   * Paste-a-booking extraction validates first, then stores through the same
   * transaction as the manual form. A 503 carries an actionable fallback.
   */
  extractTrip: (pastedBookingText: string) =>
    send<Trip>('/trips/extract', 'POST', { pasted_booking_text: pastedBookingText }),
}
