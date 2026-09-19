import { useState } from 'react'
import { formatClock, formatDelta, formatDuration, formatInr } from '../lib/format'
import { Tooltip } from './Tooltip'
import type { AgentAction, RecoveryPlan } from '../types'

interface ConfirmationCardProps {
  plan: RecoveryPlan
  /** Used only to time the recovery, first stage to last. */
  actions?: AgentAction[]
}

/** Wall-clock time from the first recorded stage to the last, as "4m 12s". */
function resolutionTime(actions: AgentAction[]) {
  if (actions.length < 2) return null
  const stamps = actions.map((action) => Date.parse(action.at)).filter(Number.isFinite)
  if (stamps.length < 2) return null
  const seconds = Math.round((Math.max(...stamps) - Math.min(...stamps)) / 1000)
  if (seconds < 0) return null
  return seconds < 60 ? `${seconds}s` : `${Math.floor(seconds / 60)}m ${String(seconds % 60).padStart(2, '0')}s`
}

function CopyableRef({ value }: { value: string }) {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value)
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {
      // Clipboard is permission-gated and blocked over plain http. The reference is
      // on screen either way, so a failure needs no error state — just no feedback.
    }
  }

  return (
    <button
      className="lift inline-flex items-center gap-2 rounded-md border border-white/25 bg-white/10 px-3 py-2 font-mono text-xs font-semibold tracking-[0.08em] text-white hover:bg-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-navy"
      onClick={copy}
      type="button"
    >
      {value}
      <span aria-live="polite" className="text-[10px] uppercase tracking-[0.12em] text-white/70">
        {copied ? 'Copied' : 'Copy'}
      </span>
    </button>
  )
}

/**
 * The end state: what the agent actually booked, and what it cost.
 *
 * Only rendered once the plan reports EXECUTED — showing this while a booking is
 * still in flight would claim a confirmation we do not have.
 */
export function ConfirmationCard({ plan, actions = [] }: ConfirmationCardProps) {
  if (plan.state !== 'EXECUTED') return null

  const chosen = plan.options.find((option) => option.id === plan.chosen_option_id)
  const elapsed = resolutionTime(actions)

  return (
    <article
      aria-labelledby="confirmation-heading"
      className="overflow-hidden rounded-lg border border-outline-variant/70 bg-surface-container-lowest shadow-raised"
    >
      <header className="bg-navy px-6 py-7 text-white">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-300">
              Recovery complete
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight" id="confirmation-heading">
              You&rsquo;re all set.
            </h2>
            <p className="mt-3 max-w-xl text-sm leading-6 text-white/75">{plan.member_message}</p>
          </div>
          <div className="shrink-0 sm:text-right">
            {elapsed && (
              <>
                <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-white/60">Resolved in</p>
                <p className="mt-1 font-mono text-2xl font-semibold">{elapsed}</p>
              </>
            )}
            <div className="mt-3">
              <CopyableRef value={plan.id} />
            </div>
          </div>
        </div>
      </header>

      {chosen && (
        <section aria-label="Rebooked flight" className="border-b border-outline-variant/60 px-6 py-6">
          <div className="flex flex-wrap items-center gap-2">
            <span className="grid size-8 place-items-center rounded bg-navy font-mono text-[11px] font-semibold text-white">
              {chosen.carrier}
            </span>
            <span className="font-mono text-sm font-semibold tracking-[0.06em]">{chosen.flight_number}</span>
            <span className="rounded-full bg-emerald-50 px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-emerald-700">
              Confirmed &amp; ticketed
            </span>
          </div>

          <div className="mt-5 grid gap-6 sm:grid-cols-[1fr_auto_1fr] sm:items-center">
            <div>
              <p className="font-mono text-3xl font-semibold leading-none">{formatClock(chosen.departure)}</p>
              <p className="mt-2 text-sm text-on-surface-variant">Departure · UTC</p>
            </div>
            <div className="text-center" aria-hidden="true">
              <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-on-surface-variant">
                {formatDuration(chosen.departure, chosen.arrival)}
              </p>
              <p className="mt-1 text-xs text-on-surface-variant">
                {chosen.stops === 0 ? 'Non-stop' : `${chosen.stops} stop${chosen.stops > 1 ? 's' : ''}`}
              </p>
            </div>
            <div className="sm:text-right">
              <p className="font-mono text-3xl font-semibold leading-none">{formatClock(chosen.arrival)}</p>
              <p className="mt-2 text-sm text-on-surface-variant">Arrival · UTC</p>
            </div>
          </div>
        </section>
      )}

      <section aria-label="Cost summary" className="grid gap-5 px-6 py-6 sm:grid-cols-3">
        <div>
          <p className="text-xs text-on-surface-variant">Fare</p>
          <p className="mt-1 text-lg font-bold">{chosen ? formatInr(chosen.fare_inr) : '—'}</p>
        </div>
        <div>
          <p className="text-xs text-on-surface-variant">Hotel impact</p>
          <p className="mt-1 text-lg font-bold">
            {plan.hotel_change.required ? formatDelta(plan.hotel_change.cost_delta_inr) : 'Untouched'}
          </p>
        </div>
        <div>
          <p className="text-xs text-on-surface-variant">
            <Tooltip label="Fare difference plus any hotel cost change, against what you originally paid.">
              <span>Net change</span>
            </Tooltip>
          </p>
          <p
            className={`mt-1 text-lg font-bold ${plan.total_cost_delta_inr <= 0 ? 'text-emerald-700' : 'text-on-surface'}`}
          >
            {formatDelta(plan.total_cost_delta_inr)}
          </p>
        </div>
      </section>
    </article>
  )
}
