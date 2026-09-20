import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { AgentTimeline } from '../components/AgentTimeline'
import { ApprovalModal } from '../components/ApprovalModal'
import { BookingImport } from '../components/BookingImport'
import { ConfirmationCard } from '../components/ConfirmationCard'
import { EmptyState } from '../components/EmptyState'
import { FlightAlternativesCard } from '../components/FlightAlternativesCard'
import { HotelPolicyCard } from '../components/HotelPolicyCard'
import { LiveFlightStatusCard } from '../components/LiveFlightStatusCard'
import { OperationsBar } from '../components/OperationsBar'
import { RadarPanel } from '../components/RadarPanel'
import { RejectionPanel } from '../components/RejectionPanel'
import { FlightAlternativesSkeleton, FlightStatusSkeleton, HotelPolicySkeleton } from '../components/Skeletons'
import { TripCard } from '../components/TripCard'
import { createRequestGate } from '../lib/requestGate'
import { apiTravelService, ApiError, type Account, type SimulationKind } from '../services/api'
import { connectLive } from '../services/live'
import type { AgentAction } from '../types'

type LoadState<T> = { data: T | null; loading: boolean; error: string | null }

function disruptionIdFrom(actions: AgentAction[]): string | null {
  for (let index = actions.length - 1; index >= 0; index -= 1) {
    const disruptionId = actions[index]?.detail?.disruption_id
    if (typeof disruptionId === 'string') return disruptionId
  }
  return null
}

function useLoad<T>(loader: () => Promise<T>, keys: unknown[]): LoadState<T> & { reload: () => void } {
  const gate = useRef(createRequestGate())
  const [attempt, setAttempt] = useState(0)
  const [state, setState] = useState<LoadState<T>>({ data: null, loading: true, error: null })
  const reload = useCallback(() => setAttempt((value) => value + 1), [])
  useEffect(() => {
    const currentGate = gate.current
    const request = currentGate.next()
    setState({ data: null, loading: true, error: null })
    void loader().then(
      (data) => { if (currentGate.isCurrent(request)) setState({ data, loading: false, error: null }) },
      (cause) => { if (currentGate.isCurrent(request)) setState({ data: null, loading: false, error: cause instanceof Error ? cause.message : 'The API did not answer.' }) },
    )
    return () => currentGate.cancel()
    // The caller owns stable loaders through route ids and explicit reloads.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...keys, attempt])
  return { ...state, reload }
}

function useLiveReload(tripId: string | undefined, reload: () => void) {
  useEffect(() => {
    if (!tripId) return
    return connectLive({
      onEvent: (event) => { if (event.trip_id === tripId) reload() },
      onPoll: reload,
      onStatus: () => {},
    })
  }, [tripId, reload])
}

function PageHead({ eyebrow, title, copy, action }: { eyebrow: string; title: string; copy?: string; action?: React.ReactNode }) {
  return <header className="page-head"><div><p>{eyebrow}</p><h1>{title}</h1>{copy && <span>{copy}</span>}</div>{action}</header>
}

function LoadError({ message, retry }: { message: string; retry: () => void }) {
  return <section className="state-panel" role="alert"><b>We could not load this page.</b><p>{message}</p><button onClick={retry} type="button">Try again</button></section>
}

async function bundle(tripId: string) {
  const [trip, actions] = await Promise.all([
    apiTravelService.getTrip(tripId), apiTravelService.getTimeline(tripId),
  ])
  return { trip, actions }
}

export function OverviewPage() {
  const state = useLoad(apiTravelService.getTrips, [])
  const [selectedTripId, setSelectedTripId] = useState<string | null>(null)
  const trip = state.data?.find((item) => item.id === selectedTripId) ?? state.data?.[0]
  const tripId = trip?.id
  const timeline = useLoad(
    () => tripId ? apiTravelService.getTimeline(tripId) : Promise.resolve([]),
    [tripId],
  )
  const reloadTrips = state.reload
  const reloadTimeline = timeline.reload
  const refresh = useCallback(() => { reloadTrips(); reloadTimeline() }, [reloadTrips, reloadTimeline])
  useLiveReload(tripId, refresh)
  const simulate = async (kind: SimulationKind) => {
    const flight = trip?.flights.find((item) => item.leg === 'outbound')
    await apiTravelService.simulate(kind, flight?.id)
    state.reload()
    timeline.reload()
  }
  return (
    <>
      <PageHead eyebrow="Journey control" title="Your trips, handled." copy="A live operational view backed by your private account." action={<Link className="primary-action" to="/app/trips/new">Add a trip</Link>} />
      {state.loading && <div className="page-stack"><FlightStatusSkeleton /><HotelPolicySkeleton /></div>}
      {state.error && <LoadError message={state.error} retry={state.reload} />}
      {!state.loading && !state.error && !trip && <EmptyState onRetry={state.reload} />}
      {!state.loading && !state.error && trip && <div className="page-stack"><OperationsBar live onSelectTrip={setSelectedTripId} onSimulate={simulate} trip={trip} trips={state.data ?? []} /><RadarPanel flights={trip.flights} status={trip.status} /><TripCard trip={trip} /><div className="page-actions"><Link to={`/app/trips/${trip.id}`}>Open trip details</Link><Link to={`/app/trips/${trip.id}/recovery`}>View recovery</Link></div>{timeline.loading ? <FlightStatusSkeleton /> : timeline.error ? <LoadError message={timeline.error} retry={timeline.reload} /> : <AgentTimeline actions={timeline.data ?? []} />}</div>}
    </>
  )
}

export function TripsPage() {
  const state = useLoad(apiTravelService.getTrips, [])
  return <><PageHead eyebrow="Itineraries" title="Trips under watch." copy="Trips persist in PostgreSQL and re-enter monitoring after a restart." action={<Link className="primary-action" to="/app/trips/new">Add a trip</Link>} />
    {state.loading && <div className="card-grid"><FlightStatusSkeleton /><FlightStatusSkeleton /></div>}
    {state.error && <LoadError message={state.error} retry={state.reload} />}
    {!state.loading && !state.error && state.data?.length === 0 && <section className="state-panel"><b>No trips yet.</b><p>Paste a confirmation or enter the first itinerary manually.</p><Link to="/app/trips/new">Create a trip</Link></section>}
    {!state.loading && !state.error && <div className="trip-list">{state.data?.map((trip) => <div key={trip.id}><TripCard trip={trip} /><div className="page-actions"><Link to={`/app/trips/${trip.id}`}>Details</Link><Link to={`/app/trips/${trip.id}/recovery`}>Recovery</Link></div></div>)}</div>}
  </>
}

export function TripDetailPage() {
  const { tripId = '' } = useParams()
  const state = useLoad(() => bundle(tripId), [tripId])
  useLiveReload(tripId, state.reload)
  const simulate = async (kind: SimulationKind) => {
    const flight = state.data?.trip.flights.find((item) => item.leg === 'outbound')
    await apiTravelService.simulate(kind, flight?.id); state.reload()
  }
  if (state.loading) return <div className="page-stack"><FlightStatusSkeleton /><HotelPolicySkeleton /></div>
  if (state.error) return <LoadError message={state.error} retry={state.reload} />
  if (!state.data) return null
  const { trip, actions } = state.data
  return <><PageHead eyebrow={`${trip.origin} → ${trip.destination}`} title={`${trip.traveller_name}'s itinerary`} action={<Link className="primary-action" to={`/app/trips/${trip.id}/recovery`}>Recovery plan</Link>} /><div className="page-stack"><OperationsBar live onSelectTrip={() => {}} onSimulate={simulate} trip={trip} trips={[trip]} /><TripCard trip={trip} /><div className="card-grid">{trip.flights.map((flight) => <LiveFlightStatusCard flight={flight} key={flight.id} />)}</div>{trip.hotels.map((hotel) => <HotelPolicyCard hotel={hotel} key={hotel.id} />)}<AgentTimeline actions={actions} /></div></>
}

export function RecoveryPage() {
  const { tripId = '' } = useParams()
  const state = useLoad(async () => {
    const { trip, actions } = await bundle(tripId)
    const disruptionId = disruptionIdFrom(actions)
    if (!disruptionId) return { trip, actions, plan: null, pending: false }
    try { return { trip, actions, plan: await apiTravelService.getPlan(disruptionId), pending: false } }
    catch (cause) { if (cause instanceof ApiError && cause.status === 404) return { trip, actions, plan: null, pending: true }; throw cause }
  }, [tripId])
  useLiveReload(tripId, state.reload)
  const [approvalOpen, setApprovalOpen] = useState(false)
  if (state.loading) return <div className="page-stack"><FlightAlternativesSkeleton /><HotelPolicySkeleton /></div>
  if (state.error) return <LoadError message={state.error} retry={state.reload} />
  if (!state.data) return null
  const { trip, actions, plan, pending } = state.data
  const decide = async (decision: 'approve' | 'reject') => { if (!plan) return; await (decision === 'approve' ? apiTravelService.approvePlan(plan.id) : apiTravelService.rejectPlan(plan.id)); setApprovalOpen(false); state.reload() }
  const simulate = async () => { const flight = trip.flights.find((item) => item.leg === 'outbound'); await apiTravelService.simulate('cancellation', flight?.id); state.reload() }
  return <><PageHead eyebrow="Recovery workspace" title="Every option, including every rejection." copy="The feed is simulated. Filtering, ranking, approval and sandbox booking logic are real." />
    {!plan && <section className="state-panel"><b>{pending ? 'The recovery plan is still being prepared.' : 'No disruption has triggered a plan yet.'}</b><p>{pending ? 'A transient plan lookup is retried here; it is not treated as a permanent failure.' : 'Use the declared demo action to cancel the outbound leg and start the real decision flow.'}</p><button onClick={() => void (pending ? Promise.resolve(state.reload()) : simulate())} type="button">{pending ? 'Check again' : 'Simulate cancellation'}</button></section>}
    {plan && <div className="page-stack">{plan.state === 'EXECUTED' && <ConfirmationCard actions={actions} plan={plan} />}<section className="decision-banner"><div><small>PLAN · {plan.state}</small><h2>{plan.approval_reason || 'Recovery plan ready'}</h2></div>{plan.state === 'AWAITING_APPROVAL' && <button onClick={() => setApprovalOpen(true)} type="button">Review decision</button>}</section>{plan.state === 'FAILED' && <section className="state-panel" role="alert"><b>Recovery needs your attention.</b><p>The concierge stopped because this plan could not be completed. The timeline below explains what happened.</p></section>}{plan.state === 'REJECTED' && <section className="state-panel"><b>You rejected this plan.</b><p>No further booking was made for this recovery plan.</p></section>}{plan.options.length ? <FlightAlternativesCard constraints={trip.constraints} plan={plan} /> : <section className="state-panel"><b>No alternative satisfies every constraint.</b><p>The concierge stopped instead of inventing a valid route. Review the reasons below.</p></section>}<RejectionPanel rejections={plan.rejections} />{trip.hotels.map((hotel) => <HotelPolicyCard change={plan.hotel_change} hotel={hotel} key={hotel.id} />)}<AgentTimeline actions={actions} /></div>}
    {approvalOpen && plan && <ApprovalModal onApprove={() => decide('approve')} onClose={() => setApprovalOpen(false)} onReject={() => decide('reject')} plan={plan} />}
  </>
}

function AdditionalTripFields() {
  return <fieldset><legend>More safeguards <small>optional</small></legend><div className="field-grid">
    <label>Fare paid for outbound (INR)<input min="0" name="fare_inr" type="number" /></label>
    <label>Cabin<select defaultValue="economy" name="cabin"><option value="economy">Economy</option><option value="business">Business</option><option value="first">First</option></select></label>
    <label>Hard arrival deadline <small>include time offset, for example 2026-10-01T15:00:00+01:00</small><input name="hard_arrival_by" placeholder="2026-10-01T15:00:00+01:00" type="text" /></label>
    <label>Deadline timezone <small>IANA name, such as Europe/London</small><input name="hard_arrival_timezone" placeholder="Europe/London" /></label>
    <label>Why the deadline matters<input name="hard_arrival_reason" placeholder="Client meeting" /></label>
    <label>Carriers to avoid <small>separate codes with commas</small><input name="avoid_carriers" placeholder="BA, EK" /></label>
  </div></fieldset>
}

export function NewTripPage() {
  const navigate = useNavigate()
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setSaving(true); setError(null)
    const data = new FormData(event.currentTarget)
    const value = (name: string) => String(data.get(name) ?? '').trim()
    try {
      const returnNumber = value('return_flight_number')
      const hotelName = value('hotel_name')
      const payload = {
        traveller_name: value('traveller_name'), origin: value('origin'), destination: value('destination'),
        outbound: { carrier: value('carrier'), flight_number: value('flight_number'), origin: value('origin'), destination: value('destination'), scheduled_departure: value('departure'), scheduled_arrival: value('arrival'), origin_timezone: value('origin_timezone') || null, destination_timezone: value('destination_timezone') || null, booking_reference: value('booking_reference') || null, fare_inr: value('fare_inr') ? Number(value('fare_inr')) : null, cabin: value('cabin') || 'economy' },
        return_flight: returnNumber ? { carrier: value('return_carrier'), flight_number: returnNumber, origin: value('destination'), destination: value('origin'), scheduled_departure: value('return_departure'), scheduled_arrival: value('return_arrival'), origin_timezone: value('destination_timezone') || null, destination_timezone: value('origin_timezone') || null, booking_reference: value('booking_reference') || null } : null,
        hotel: hotelName ? { name: hotelName, city: value('hotel_city'), city_timezone: value('hotel_timezone') || null, check_in: value('hotel_check_in'), check_out: value('hotel_check_out'), confirmation_number: value('hotel_confirmation') || null, nightly_rate_inr: value('hotel_rate') ? Number(value('hotel_rate')) : null, modifiable: true } : null,
        constraints: { max_fare_inr: value('max_fare_inr') ? Number(value('max_fare_inr')) : null, max_stops: Number(value('max_stops') || 1), auto_approve_under_inr: value('auto_approve') ? Number(value('auto_approve')) : null, cabin: value('cabin') || 'economy', hard_arrival_by: value('hard_arrival_by') || null, hard_arrival_timezone: value('hard_arrival_timezone') || null, hard_arrival_reason: value('hard_arrival_reason') || null, avoid_carriers: value('avoid_carriers').split(',').map((code) => code.trim().toUpperCase()).filter(Boolean) },
      }
      const trip = await apiTravelService.createTrip(payload); navigate(`/app/trips/${trip.id}`)
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Trip creation failed.') } finally { setSaving(false) }
  }
  return <><PageHead eyebrow="New itinerary" title="Add a trip to monitoring." copy="Enter the booking manually or paste a confirmation. Both paths persist through the same transaction." /><div className="new-trip-grid"><form className="trip-form" onSubmit={(event) => void submit(event)}><h2>Manual trip</h2><fieldset><legend>Outbound flight</legend><div className="field-grid"><label>Traveller name<input name="traveller_name" required /></label><label>Carrier<input maxLength={3} name="carrier" placeholder="AI" required /></label><label>Origin IATA<input maxLength={3} name="origin" placeholder="BOM" required /></label><label>Destination IATA<input maxLength={3} name="destination" placeholder="LHR" required /></label><label>Flight number<input name="flight_number" placeholder="AI131" required /></label><label>Booking reference<input name="booking_reference" /></label><label>Departure<input name="departure" required type="datetime-local" /></label><label>Arrival<input name="arrival" required type="datetime-local" /></label><label>Origin timezone <small>required for unknown airports</small><input name="origin_timezone" placeholder="America/New_York" /></label><label>Destination timezone <small>required for unknown airports</small><input name="destination_timezone" placeholder="Asia/Tokyo" /></label></div></fieldset><fieldset><legend>Return flight <small>optional</small></legend><div className="field-grid"><label>Carrier<input maxLength={3} name="return_carrier" /></label><label>Flight number<input name="return_flight_number" /></label><label>Departure<input name="return_departure" type="datetime-local" /></label><label>Arrival<input name="return_arrival" type="datetime-local" /></label></div></fieldset><fieldset><legend>Hotel <small>optional</small></legend><div className="field-grid"><label>Hotel name<input name="hotel_name" /></label><label>City or IATA<input name="hotel_city" placeholder="LON" /></label><label>City timezone<input name="hotel_timezone" placeholder="Europe/London" /></label><label>Confirmation<input name="hotel_confirmation" /></label><label>Check-in<input name="hotel_check_in" type="date" /></label><label>Check-out<input name="hotel_check_out" type="date" /></label><label>Nightly rate (INR)<input min="0" name="hotel_rate" type="number" /></label></div></fieldset><fieldset><legend>Safeguards</legend><div className="field-grid"><label>Fare cap (INR)<input min="0" name="max_fare_inr" type="number" /></label><label>Auto-approve under (INR)<input min="0" name="auto_approve" type="number" /></label><label>Maximum stops<input defaultValue="1" max="4" min="0" name="max_stops" type="number" /></label></div></fieldset><AdditionalTripFields /><p aria-live="polite" className="form-error">{error}</p><button disabled={saving} type="submit">{saving ? 'Saving trip…' : 'Save and monitor'}</button></form><BookingImport live onExtract={async (text) => { const trip = await apiTravelService.extractTrip(text); navigate(`/app/trips/${trip.id}`); return trip }} /></div></>
}

export function ProfilePage({ account, onLogout }: { account: Account; onLogout: () => Promise<void> }) {
  const state = useLoad(apiTravelService.getTrips, [])
  const constraints = state.data?.[0]?.constraints
  return <><PageHead eyebrow="Account" title="Profile & safeguards." />{state.loading && <FlightStatusSkeleton />}{state.error && <LoadError message={state.error} retry={state.reload} />}{!state.loading && !state.error && <section className="profile-page"><div className="profile-identity"><img alt="ATC logo" src="/assets/atc-logo.png" /><div><h2>{account.name}</h2><p>{account.email}</p></div></div>{state.data?.length === 0 && <p>No trips yet. Add one to set traveller safeguards.</p>}<dl><div><dt>Fare cap</dt><dd>{constraints?.max_fare_inr != null ? `₹${constraints.max_fare_inr.toLocaleString('en-IN')}` : 'Not set'}</dd></div><div><dt>Maximum stops</dt><dd>{constraints?.max_stops ?? 'Not set'}</dd></div><div><dt>Cabin</dt><dd>{constraints?.cabin ?? 'Not set'}</dd></div><div><dt>Auto-approve</dt><dd>{constraints?.auto_approve_under_inr != null ? `₹${constraints.auto_approve_under_inr.toLocaleString('en-IN')}` : 'Not set'}</dd></div></dl><p>Safeguards are applied by deterministic policy code. The optional model only narrates the decision.</p><button onClick={() => void onLogout()} type="button">Log out</button></section>}</>
}

export function AppNotFound() {
  return <section className="app-not-found"><div aria-hidden="true" className="broken-route">404</div><p>Route unavailable</p><h1>This path is outside your itinerary.</h1><Link to="/app">Return to overview</Link></section>
}
