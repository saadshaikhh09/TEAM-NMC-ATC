import { formatClock, formatDuration, formatInr } from '../lib/format'
import { Tooltip } from './Tooltip'
import type { Constraints, FlightOption, RecoveryPlan } from '../types'

interface FlightAlternativesCardProps {
  plan: RecoveryPlan
  /** Used only to explain *why* an option passed — the filtering already happened server-side. */
  constraints?: Constraints
}

function OptionRow({
  chosen,
  option,
  rank,
  withinFareCap,
}: {
  chosen: boolean
  option: FlightOption
  rank: number
  withinFareCap: boolean
}) {
  const duration = formatDuration(option.departure, option.arrival)

  return (
    <li
      className={`lift rounded-md border bg-surface-container-lowest p-5 ${
        chosen ? 'border-primary/60 ring-1 ring-primary/30' : 'border-outline-variant/60 hover:border-outline-variant'
      }`}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="grid size-8 shrink-0 place-items-center rounded bg-navy font-mono text-[11px] font-semibold text-white">
              {option.carrier}
            </span>
            <span className="font-mono text-sm font-semibold tracking-[0.06em]">{option.flight_number}</span>
            {chosen && (
              <span className="rounded-full bg-primary px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-white">
                Agent&rsquo;s choice
              </span>
            )}
            <span className="rounded-full bg-surface-container px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-on-surface-variant">
              {option.stops === 0 ? 'Non-stop' : `${option.stops} stop${option.stops > 1 ? 's' : ''}`}
            </span>
          </div>

          <div className="mt-4 flex items-center gap-3">
            <span className="font-mono text-xl font-semibold">{formatClock(option.departure)}</span>
            <span className="flex flex-1 items-center gap-2 text-on-surface-variant" aria-hidden="true">
              <span className="h-px flex-1 bg-outline-variant" />
              <span className="font-mono text-[10px] uppercase tracking-[0.1em]">{duration}</span>
              <span className="h-px flex-1 bg-outline-variant" />
            </span>
            <span className="font-mono text-xl font-semibold">{formatClock(option.arrival)}</span>
          </div>
          <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.12em] text-on-surface-variant">
            {option.cabin} · Option {rank} · departs UTC
          </p>
        </div>

        <div className="shrink-0 sm:text-right">
          <p className="text-xl font-bold tracking-tight">{formatInr(option.fare_inr)}</p>
          <p
            className={`mt-1 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] ${
              withinFareCap ? 'text-emerald-700' : 'text-warning'
            }`}
          >
            {withinFareCap ? 'Within fare cap' : 'Over fare cap'}
          </p>
        </div>
      </div>
    </li>
  )
}

/**
 * The options that survived the policy filter, chosen option first.
 *
 * Pairs with RejectionPanel: this card is what the agent *can* do, that one is what
 * it refused to do. Showing the survivors without the count of what was evaluated
 * would make the agent look lucky rather than thorough, so the header carries both.
 */
export function FlightAlternativesCard({ plan, constraints }: FlightAlternativesCardProps) {
  if (plan.options.length === 0) return null

  // `== null` deliberately: the API sends null for "no ceiling", and a `!== undefined`
  // check would treat that as a cap of zero and brand every surviving option as a breach.
  const fareCap = constraints?.max_fare_inr ?? null
  // Chosen option leads, the rest keep the server's ranking behind it.
  const ordered = [...plan.options].sort((a, b) => {
    if (a.id === plan.chosen_option_id) return -1
    if (b.id === plan.chosen_option_id) return 1
    return 0
  })

  return (
    <article
      aria-labelledby="alternatives-heading"
      className="overflow-hidden rounded-lg border border-outline-variant/70 bg-surface-container-lowest shadow-card"
    >
      <header className="flex flex-col gap-4 border-b border-outline-variant/60 bg-surface-container-low px-6 py-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">
            Recovery options
          </p>
          <h2 className="mt-2 text-2xl font-bold tracking-tight" id="alternatives-heading">
            {plan.options.length} route{plan.options.length === 1 ? '' : 's'} clear your rules
          </h2>
          <p className="mt-2 text-sm leading-6 text-on-surface-variant">
            <Tooltip label="Every option the agent retrieved from the provider before any filtering.">
              <span>{plan.evaluated_count} evaluated</span>
            </Tooltip>
            {' · '}
            <Tooltip label="Options discarded because they broke a rule you set. Each refusal is listed below with its reason.">
              <span>
                {plan.rejections.length} rejected on policy
              </span>
            </Tooltip>
          </p>
        </div>
        {fareCap !== null && (
          <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-on-surface-variant">
            Fare cap {formatInr(fareCap)}
          </p>
        )}
      </header>

      <ul className="space-y-3 p-6">
        {ordered.map((option, index) => (
          <OptionRow
            chosen={option.id === plan.chosen_option_id}
            key={option.id}
            option={option}
            rank={index + 1}
            withinFareCap={fareCap === null || option.fare_inr <= fareCap}
          />
        ))}
      </ul>
    </article>
  )
}
