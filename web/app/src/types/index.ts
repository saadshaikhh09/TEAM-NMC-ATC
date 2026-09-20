export type TripStatus =
  | 'CREATED'
  | 'MONITORING'
  | 'DISRUPTED'
  | 'PLANNING'
  | 'AWAITING_APPROVAL'
  | 'EXECUTING'
  | 'RECOVERED'
  | 'RECOVERY_FAILED'

export type FlightLeg = 'outbound' | 'return'
export type FlightStatus = 'SCHEDULED' | 'DELAYED' | 'CANCELLED' | 'DEPARTED' | 'LANDED'

export interface Flight {
  id: string
  leg: FlightLeg
  carrier: string
  flight_number: string
  origin: string
  destination: string
  scheduled_departure: string
  scheduled_arrival: string
  departure_local: string
  arrival_local: string
  status: FlightStatus
  /** Null once the flight is disrupted or terminal — the monitor stops scheduling polls. */
  next_poll_at: string | null
}

export interface Hotel {
  id: string
  provider: string
  confirmation_number: string | null
  name: string
  city: string
  check_in: string
  check_out: string
  nightly_rate_inr: number | null
  modifiable: boolean
  status: 'CONFIRMED'
}

export interface Constraints {
  hard_arrival_by: string
  hard_arrival_by_local: string | null
  hard_arrival_reason: string
  /** Null means the traveller set no fare ceiling, not a ceiling of zero. */
  max_fare_inr: number | null
  max_stops: number
  cabin: string
  avoid_carriers: string[]
  auto_approve_under_inr: number
}

export interface Trip {
  id: string
  traveller_name: string
  status: TripStatus
  origin: string
  destination: string
  flights: Flight[]
  hotels: Hotel[]
  constraints: Constraints
}

export type DisruptionKind = 'CANCELLATION' | 'DELAY' | 'SCHEDULE_CHANGE'
export type DisruptionSource = 'simulated' | 'aerodatabox' | 'aviationstack' | 'duffel'

export interface Disruption {
  id: string
  trip_id: string
  flight_id: string
  kind: DisruptionKind
  source: DisruptionSource
  detected_at: string
  previous_status: FlightStatus
  new_status: FlightStatus
}

export interface FlightOption {
  id: string
  carrier: string
  flight_number: string
  departure: string
  arrival: string
  stops: number
  cabin: string
  fare_inr: number
}

export interface Rejection {
  option_id: string
  rule: string
  human_reason: string
  note: string
}

export type RecoveryPlanState =
  | 'DRAFT'
  | 'AWAITING_APPROVAL'
  | 'APPROVED'
  | 'REJECTED'
  | 'EXECUTING'
  | 'EXECUTED'
  | 'FAILED'

export interface HotelChange {
  required: boolean
  new_check_in: string
  cost_delta_inr: number
}

export interface RecoveryPlan {
  id: string
  disruption_id: string
  state: RecoveryPlanState
  evaluated_count: number
  options: FlightOption[]
  rejections: Rejection[]
  /** Null until an option survives the constraint filter — a rejection-only plan has none. */
  chosen_option_id: string | null
  /** Null when the trip has no hotel, or no option was chosen to price a move against. */
  hotel_change: HotelChange | null
  /** Null on a rejection-only plan. Null is "not calculated", never zero. */
  total_cost_delta_inr: number | null
  requires_approval: boolean
  approval_reason: string
  explanation: string
  member_message: string
}

export type AgentStage =
  | 'DETECTED'
  | 'PLANNING'
  | 'EVALUATED'
  | 'AWAITING_APPROVAL'
  | 'APPROVED'
  | 'REBOOKED'
  | 'HOTEL_SHIFTED'
  | 'NOTIFIED'
  | 'FAILED'

export interface AgentAction {
  id: string
  trip_id: string
  at: string
  stage: AgentStage
  headline: string
  detail: Record<string, unknown>
  /** Null when the stage did not record a timing — no `record()` call site sets it yet. */
  duration_ms: number | null
}

export type WsEventType =
  | 'trip.updated'
  | 'disruption.detected'
  | 'plan.ready'
  | 'plan.awaiting_approval'
  | 'plan.executing'
  | 'plan.executed'
  | 'plan.failed'
  | 'action.recorded'

export interface WsEvent {
  type: WsEventType
  trip_id: string
  payload: Record<string, unknown>
}
