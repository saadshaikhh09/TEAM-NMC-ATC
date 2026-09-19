import type { Disruption, RecoveryPlan } from '../types'

export const disruption: Disruption = {
  id: 'uuid',
  trip_id: 'uuid',
  flight_id: 'uuid',
  kind: 'CANCELLATION',
  source: 'simulated',
  detected_at: '2026-09-19T08:33:11+00:00',
  previous_status: 'SCHEDULED',
  new_status: 'CANCELLED',
}

export const recoveryPlan: RecoveryPlan = {
  id: 'uuid',
  disruption_id: 'uuid',
  state: 'AWAITING_APPROVAL',
  evaluated_count: 14,
  options: [
    {
      id: 'opt_1',
      carrier: 'BA',
      flight_number: 'BA138',
      departure: '2026-09-20T08:10:00+00:00',
      arrival: '2026-09-20T18:05:00+00:00',
      stops: 0,
      cabin: 'economy',
      fare_inr: 52400,
    },
    {
      id: 'opt_2',
      carrier: 'VS',
      flight_number: 'VS355',
      departure: '2026-09-20T09:45:00+00:00',
      arrival: '2026-09-20T20:20:00+00:00',
      stops: 0,
      cabin: 'economy',
      fare_inr: 57900,
    },
    {
      id: 'opt_3',
      carrier: 'EK',
      flight_number: 'EK507',
      departure: '2026-09-20T04:30:00+00:00',
      arrival: '2026-09-20T19:10:00+00:00',
      stops: 1,
      cabin: 'economy',
      fare_inr: 44150,
    },
  ],
  rejections: [
    {
      option_id: 'opt_4',
      rule: 'hard_arrival_by',
      human_reason: 'Arrives 11:40, misses hard deadline 09:00',
      note: 'would have been 8,000 cheaper',
    },
    {
      option_id: 'opt_5',
      rule: 'max_stops',
      human_reason: 'Two stops via DXB and FRA, limit is 1',
      note: 'cheapest option found, 38,200',
    },
    {
      option_id: 'opt_6',
      rule: 'max_fare_inr',
      human_reason: 'Fare 71,300 exceeds your cap of 60,000',
      note: 'would have arrived 3 hours earlier',
    },
  ],
  chosen_option_id: 'opt_1',
  hotel_change: {
    required: true,
    new_check_in: '2026-09-21',
    cost_delta_inr: -9800,
  },
  total_cost_delta_inr: 4200,
  requires_approval: true,
  approval_reason: 'fare 52,400 exceeds auto-approve threshold 45,000',
  explanation: 'LLM prose, may be a templated fallback',
  member_message: 'LLM prose, may be a templated fallback',
}
