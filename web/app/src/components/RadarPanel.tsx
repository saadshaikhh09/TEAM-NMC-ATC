import { Tooltip } from './Tooltip'
import type { Flight, TripStatus } from '../types'

interface RadarPanelProps {
  flights: Flight[]
  status: TripStatus
}

/** Statuses where the agent is actively holding the trip rather than acting on it. */
const WATCHING: ReadonlySet<TripStatus> = new Set<TripStatus>(['CREATED', 'MONITORING'])

/**
 * The monitor, as a picture.
 *
 * Purely decorative — every number beside it is also stated in text, so the radar
 * carries no information a screen reader would lose. It is hidden from the
 * accessibility tree for exactly that reason.
 */
function Radar({ active, blips }: { active: boolean; blips: number }) {
  return (
    <div className="relative size-32 shrink-0" aria-hidden="true">
      <svg className="size-full" viewBox="0 0 100 100">
        {[46, 32, 18].map((r) => (
          <circle cx="50" cy="50" fill="none" key={r} r={r} stroke="#c2c6d8" strokeOpacity="0.6" strokeWidth="0.7" />
        ))}
        <line stroke="#c2c6d8" strokeOpacity="0.6" strokeWidth="0.7" x1="4" x2="96" y1="50" y2="50" />
        <line stroke="#c2c6d8" strokeOpacity="0.6" strokeWidth="0.7" x1="50" x2="50" y1="4" y2="96" />

        {active && (
          <g className="radar-sweep">
            <defs>
              <linearGradient id="radar-fade" x1="0" x2="1" y1="0" y2="0">
                <stop offset="0%" stopColor="#0066ff" stopOpacity="0.35" />
                <stop offset="100%" stopColor="#0066ff" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path d="M50 50 L96 50 A46 46 0 0 0 63 6 Z" fill="url(#radar-fade)" />
            <line stroke="#0066ff" strokeWidth="1" x1="50" x2="96" y1="50" y2="50" />
          </g>
        )}

        {Array.from({ length: blips }, (_, index) => {
          const angle = (index / Math.max(blips, 1)) * Math.PI * 2 + 0.6
          return (
            <circle
              cx={50 + Math.cos(angle) * 28}
              cy={50 + Math.sin(angle) * 28}
              fill={active ? '#0050cb' : '#727687'}
              key={index}
              r="2.6"
            />
          )
        })}
      </svg>
    </div>
  )
}

/**
 * Ambient proof that the monitor is running, with the numbers that back it up.
 *
 * Sits above the fold so the dashboard says "I am watching this" before the user
 * scrolls into anything that has gone wrong.
 */
export function RadarPanel({ flights, status }: RadarPanelProps) {
  const active = WATCHING.has(status)
  const disrupted = flights.filter((flight) => flight.status === 'CANCELLED' || flight.status === 'DELAYED')

  return (
    <section
      aria-labelledby="radar-heading"
      className="lift flex flex-col items-center gap-6 rounded-lg border border-outline-variant/70 bg-surface-container-lowest p-6 shadow-card sm:flex-row"
    >
      <Radar active={active} blips={flights.length} />

      <div className="min-w-0 flex-1 text-center sm:text-left">
        <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">
          Autonomous monitor
        </p>
        <h2 className="mt-2 text-xl font-bold tracking-tight" id="radar-heading">
          {status === 'RECOVERED' ? 'Recovery confirmed' : active
            ? `Watching ${flights.length} leg${flights.length === 1 ? '' : 's'}`
            : 'Acting on a disruption'}
        </h2>
        <p className="mt-2 text-sm leading-6 text-on-surface-variant">
          {status === 'RECOVERED' ? 'The replacement flight is recorded with its sandbox confirmation. The original disruption remains visible in the timeline.' : active
            ? 'No action needed. The agent re-checks each leg on a tiered schedule and wakes only when a status actually changes.'
            : 'A leg changed status. Planning and recovery have taken over from monitoring.'}
        </p>

        <dl className="mt-5 flex flex-wrap justify-center gap-x-8 gap-y-3 sm:justify-start">
          <div>
            <dt className="font-mono text-[10px] uppercase tracking-[0.12em] text-on-surface-variant">Legs</dt>
            <dd className="mt-1 font-mono text-lg font-semibold">{flights.length}</dd>
          </div>
          <div>
            <dt className="font-mono text-[10px] uppercase tracking-[0.12em] text-on-surface-variant">Disrupted</dt>
            <dd className={`mt-1 font-mono text-lg font-semibold ${disrupted.length ? 'text-error' : ''}`}>
              {disrupted.length}
            </dd>
          </div>
          <div>
            <dt className="font-mono text-[10px] uppercase tracking-[0.12em] text-on-surface-variant">
              <Tooltip label="The trip's position in the recovery state machine. Monitoring means nothing is wrong.">
                <span>Trip state</span>
              </Tooltip>
            </dt>
            <dd className="mt-1 font-mono text-lg font-semibold">{status}</dd>
          </div>
        </dl>
      </div>
    </section>
  )
}
