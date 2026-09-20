import type { ReactNode } from 'react'
import { Icon } from '../components/Icon'
import { Reveal } from '../components/Reveal'

/**
 * The five stages below are the real pipeline, in the order the code runs them:
 * monitor/poller → monitor/detection → planner/{constraints,hotel_impact,rank}
 * → executor/gate → executor/run. Nothing here describes a capability that is
 * not in the repository.
 */
const HEADLINE_METRICS = [
  { label: 'POLLING', labelClass: 'text-[#0284C7]', value: '12h → 6h → 15min, by proximity' },
  { label: 'BUDGET', labelClass: 'text-emerald-600', value: '500 status calls/month, hard-capped' },
  { label: 'DEFAULT', labelClass: 'text-[#0A2540]', value: 'Mock providers until you opt out' },
]

interface PhaseProps {
  phase: string
  meta: string
  title: string
  body: ReactNode
  chips: { icon: string; label: string }[]
  statusDotClass: string
  status: string
  metric: string
  visual: ReactNode
  delayMs?: number
}

function Phase({
  phase,
  meta,
  title,
  body,
  chips,
  statusDotClass,
  status,
  metric,
  visual,
  delayMs,
}: PhaseProps) {
  return (
    <Reveal
      className="group overflow-hidden rounded-3xl border border-[#DDE3EA] bg-white shadow-sm transition-all duration-300 hover:border-[#0284C7]/50 hover:shadow-xl"
      delayMs={delayMs}
    >
      <div className="flex flex-col items-stretch justify-between gap-10 p-8 sm:p-10 lg:flex-row lg:p-12">
        <div className="flex flex-1 flex-col justify-between">
          <div>
            <div className="mb-4 flex flex-wrap items-center gap-3">
              <span className="rounded-md bg-[#E0F2FE] px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider text-[#0284C7]">
                {phase}
              </span>
              <span className="font-mono text-xs text-slate-400">{meta}</span>
            </div>
            <h3 className="mb-4 font-display text-[28px] font-semibold leading-tight text-[#0A2540] transition-colors group-hover:text-[#0284C7] sm:text-[34px]">
              {title}
            </h3>
            <p className="mb-6 text-sm leading-relaxed text-[#64748B] sm:text-base">{body}</p>
            <ul className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {chips.map((chip) => (
                <li
                  className="flex items-center gap-2.5 rounded-xl border border-[#64748B]/15 bg-[#F8FAFC] p-3 text-xs font-medium text-[#0A2540]"
                  key={chip.label}
                >
                  <Icon className="text-[18px] text-[#0284C7]" name={chip.icon} />
                  {chip.label}
                </li>
              ))}
            </ul>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-[#64748B]/15 pt-4 font-mono text-xs text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className={`size-2 rounded-full ${statusDotClass}`} />
              {status}
            </span>
            <span className="font-semibold text-[#0A2540]">{metric}</span>
          </div>
        </div>
        <div className="shrink-0 lg:w-[480px]">{visual}</div>
      </div>
    </Reveal>
  )
}

export function HowItWorks() {
  return (
    <section
      className="w-full border-b border-[#64748B]/15 bg-gradient-to-b from-[#F8FAFC] via-[#EEF4F9] to-[#F8FAFC] px-4 py-28 sm:px-6 lg:px-12"
      id="how-it-works"
    >
      <div className="mx-auto max-w-[1400px]">
        <Reveal className="mx-auto mb-20 max-w-3xl text-center">
          <p className="mb-3 inline-flex items-center gap-2 rounded-full bg-[#E0F2FE] px-3.5 py-1 font-mono text-[11px] font-bold uppercase tracking-wider text-[#0284C7]">
            <span className="size-1.5 animate-ping rounded-full bg-[#0284C7]" />
            How the agent runs
          </p>
          <h2 className="mb-5 font-display text-[40px] leading-[48px] tracking-tight text-[#0A2540] sm:text-[48px] sm:leading-[56px]">
            Five stages, and you can read every one
          </h2>
          <p className="text-base leading-relaxed text-[#64748B] sm:text-lg">
            The agent is not a black box. Each stage writes a row to the trip timeline as it runs,
            so what you see on screen is the audit log, not a summary of it.
          </p>
          <ul className="mt-8 flex flex-wrap items-center justify-center gap-4 font-mono text-xs text-[#0A2540] sm:gap-8">
            {HEADLINE_METRICS.map((metric) => (
              <li
                className="flex items-center gap-2 rounded-xl border border-[#64748B]/20 bg-white px-4 py-2"
                key={metric.label}
              >
                <span className={`font-bold ${metric.labelClass}`}>{metric.label}</span>
                <span className="text-slate-500">{metric.value}</span>
              </li>
            ))}
          </ul>
        </Reveal>

        <div className="flex w-full flex-col gap-8">
          <Phase
            chips={[
              { icon: 'schedule', label: 'Cadence tightens as departure nears' },
              { icon: 'restart_alt', label: 'Resumable — state lives in the database' },
            ]}
            meta="monitor/poller.py"
            metric="500 calls/month, enforced in code"
            phase="Stage 01 • Poll"
            status="Mock provider by default; live status is opt-in"
            statusDotClass="bg-emerald-500"
            title="Check each flight on a schedule that tightens"
            visual={<PollVisual />}
            body={
              <>
                Flights more than a week out are checked twice a day, inside a week every six hours,
                and inside the last day every fifteen minutes. The next check time is a column on
                the flight row, so the process can be killed and restarted without losing its place.
                Every live call is metered against a monthly budget that{' '}
                <strong className="font-semibold text-[#0A2540]">core/quota.py</strong> refuses to
                exceed.
              </>
            }
          />

          <Phase
            chips={[
              { icon: 'account_tree', label: 'Trip moves MONITORING → DISRUPTED' },
              { icon: 'bolt', label: 'Pushed to the browser over a WebSocket' },
            ]}
            delayMs={60}
            meta="monitor/detection.py"
            metric="One disruption row, written once"
            phase="Stage 02 • Detect"
            status="Duplicate detections return the existing row"
            statusDotClass="bg-[#0284C7]"
            title="Record the disruption and move the trip"
            visual={<DetectVisual />}
            body="A status that comes back CANCELLED or DELAYED when it was not before becomes a disruption row, a state transition the state machine has to allow, and a timeline entry. The same event is pushed to any open dashboard so the screen changes without a refresh."
          />

          <Phase
            chips={[
              { icon: 'filter_alt', label: 'Each rejection carries a plain-English reason' },
              { icon: 'hotel', label: 'Hotel cost delta folded into the score' },
            ]}
            delayMs={120}
            meta="planner/constraints.py · rank.py"
            metric="Rejections are shown, not hidden"
            phase="Stage 03 • Filter and rank"
            status="Constraints come from the traveller's own row"
            statusDotClass="bg-emerald-500"
            title="Throw out what breaks your rules, rank what is left"
            visual={<RankVisual />}
            body={
              <>
                Options are filtered against the traveller's constraints — fare ceiling, maximum
                stops, cabin, carriers to avoid, and a hard arrival deadline — then scored on
                arrival time, fare and stops. If a later arrival forces a hotel change, that cost is
                added to the option before it is ranked.{' '}
                <strong className="font-semibold text-[#0A2540]">
                  Every rejected option stays on screen with the reason it lost
                </strong>
                , which is the part that makes the decision checkable.
              </>
            }
          />

          <Phase
            chips={[
              { icon: 'rule', label: 'Threshold is per traveller, not global' },
              { icon: 'front_hand', label: 'Over the limit, nothing is booked without you' },
            ]}
            delayMs={180}
            meta="executor/gate.py"
            metric="Two paths, one decision"
            phase="Stage 04 • Gate"
            status="The reason for the decision is recorded either way"
            statusDotClass="bg-emerald-500"
            title="Decide whether it may act alone"
            visual={<GateVisual />}
            body="Each traveller sets the cost change they are willing to have handled without being asked. Under it, the plan executes straight away. Over it — or when the plan touches a hard constraint — the trip parks in AWAITING_APPROVAL and waits for a decision, with the full option list and the rejections already on screen."
          />

          <Phase
            chips={[
              { icon: 'flight_takeoff', label: 'Flight booked through the search provider' },
              { icon: 'event_repeat', label: 'Hotel dates changed by cancel-then-rebook' },
            ]}
            delayMs={240}
            meta="executor/run.py"
            metric="Confirmation lands on the timeline"
            phase="Stage 05 • Execute"
            status="Runs against test and sandbox environments"
            statusDotClass="bg-emerald-500"
            title="Book it, and fix the nights that moved"
            visual={<ExecuteVisual />}
            body="The chosen option is booked and, if the new arrival pushes past check-in, the hotel booking is rebuilt at the new dates — the hotel API has no date-change call, so it is cancelled and rebooked in one step. Both confirmations are appended to the trip timeline, which is the same log every earlier stage wrote to."
          />
        </div>
      </div>
    </section>
  )
}

function PollVisual() {
  const rows = [
    { window: '> 7 days out', cadence: 'every 12 hours' },
    { window: '1 – 7 days out', cadence: 'every 6 hours' },
    { window: '< 24 hours out', cadence: 'every 15 minutes', highlight: true },
  ]

  return (
    <div className="relative flex h-full flex-col justify-between overflow-hidden rounded-2xl border border-[#0F3254] bg-[#0A2540] p-6 font-mono text-xs text-white shadow-inner">
      <div className="pointer-events-none absolute -right-16 -top-16 size-40 rounded-full bg-[#0284C7]/20 blur-2xl" />
      <div>
        <div className="mb-3 flex items-center justify-between gap-2 border-b border-white/10 pb-3">
          <span className="flex items-center gap-2 text-[11px] text-slate-300">
            <Icon className="text-[14px] text-emerald-400" name="schedule" />
            POLL CADENCE
          </span>
          <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-300">
            monitor/scheduler.py
          </span>
        </div>
        <dl className="space-y-2.5 text-[11px]">
          {rows.map((row) => (
            <div
              className={`flex justify-between gap-3 rounded border p-2 ${
                row.highlight
                  ? 'border-emerald-500/30 bg-emerald-900/30'
                  : 'border-white/10 bg-white/5'
              }`}
              key={row.window}
            >
              <dt className="text-slate-300">{row.window}</dt>
              <dd
                className={`font-semibold ${row.highlight ? 'text-emerald-300' : 'text-[#7DD3FC]'}`}
              >
                {row.cadence}
              </dd>
            </div>
          ))}
        </dl>
      </div>
      <div className="mt-6 flex items-center justify-between border-t border-white/10 pt-4 text-[11px] text-slate-400">
        <span>Three travellers, one flight each</span>
        <span className="font-semibold text-emerald-400">≈ 96 calls/flight/day at the top tier</span>
      </div>
    </div>
  )
}

function DetectVisual() {
  return (
    <div className="flex h-full flex-col justify-between rounded-2xl border border-[#64748B]/20 bg-[#F8FAFC] p-6">
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3 rounded-xl border border-red-200 bg-white p-3.5">
          <div className="flex items-center gap-3">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-red-100 text-red-600">
              <Icon className="text-[18px]" name="warning" />
            </span>
            <div>
              <span className="block text-xs font-bold text-red-900">
                Status changed to CANCELLED
              </span>
              <span className="text-[11px] text-red-700">
                Disruption row written · trip now DISRUPTED
              </span>
            </div>
          </div>
          <span className="shrink-0 rounded border border-red-200 bg-red-50 px-2 py-0.5 font-mono text-[10px] font-bold text-red-700">
            DETECTED
          </span>
        </div>
        <div className="flex items-center gap-3 rounded-xl border border-[#64748B]/15 bg-white p-3.5">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-[#0284C7] text-white">
            <Icon className="text-[18px]" name="bolt" />
          </span>
          <div className="min-w-0">
            <span className="block text-xs font-semibold text-[#0A2540]">
              disruption.detected published
            </span>
            <span className="block truncate text-[11px] text-[#64748B]">
              Open dashboards update without a refresh
            </span>
          </div>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between border-t border-[#64748B]/15 pt-3 font-mono text-[11px] text-[#64748B]">
        <span>Transition checked by the state machine</span>
        <span className="font-semibold text-emerald-600">Idempotent</span>
      </div>
    </div>
  )
}

function RankVisual() {
  const kept = [
    { label: 'Rank 1 · departs 19:40', value: 'Score 98.4', valueClass: 'text-emerald-400' },
    { label: 'Rank 2 · departs 20:15', value: 'Score 91.2', valueClass: 'text-[#7DD3FC]' },
  ]
  const rejected = [
    { label: 'Two stops', value: 'over your 1-stop limit' },
    { label: 'Arrives 11:20', value: 'after your 09:00 deadline' },
    { label: '₹48,000', value: 'over your ₹35,000 fare cap' },
  ]

  return (
    <div className="flex h-full flex-col justify-between rounded-2xl border border-[#0F3254] bg-[#0A2540] p-6 font-mono text-xs text-white">
      <div>
        <div className="mb-3 flex items-center justify-between gap-2 border-b border-white/10 pb-3">
          <span className="text-[11px] text-slate-300">6 EVALUATED</span>
          <span className="font-bold text-[#38BDF8]">3 KEPT · 3 REJECTED</span>
        </div>
        <dl className="space-y-2 text-[11px]">
          {kept.map((row) => (
            <div
              className="flex justify-between gap-3 rounded border border-white/10 bg-white/5 p-2"
              key={row.label}
            >
              <dt className="text-slate-300">{row.label}</dt>
              <dd className={`font-semibold ${row.valueClass}`}>{row.value}</dd>
            </div>
          ))}
          {rejected.map((row) => (
            <div
              className="flex justify-between gap-3 rounded border border-red-500/20 bg-red-900/20 p-2"
              key={row.label}
            >
              <dt className="text-slate-400 line-through">{row.label}</dt>
              <dd className="text-right font-semibold text-red-300">{row.value}</dd>
            </div>
          ))}
        </dl>
      </div>
      <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-3 text-[11px] text-slate-400">
        <span>Reasons are written for a person</span>
        <span className="font-semibold text-emerald-300">Shown, never hidden</span>
      </div>
    </div>
  )
}

function GateVisual() {
  return (
    <div className="flex h-full flex-col justify-between rounded-2xl border border-[#64748B]/20 bg-[#F8FAFC] p-6">
      <div className="rounded-xl border border-[#64748B]/15 bg-white p-5">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#64748B]/15 pb-3">
          <span className="flex items-center gap-2">
            <span className="size-2.5 animate-pulse rounded-full bg-emerald-500" />
            <span className="text-sm font-bold text-[#0A2540]">GATE DECISION</span>
          </span>
          <span className="font-mono text-xs font-bold text-[#0284C7]">AUTO</span>
        </div>
        <dl className="mt-4 space-y-2 font-mono text-xs">
          <div className="flex justify-between gap-3">
            <dt className="text-[#64748B]">Net cost change</dt>
            <dd className="font-bold text-[#0A2540]">+₹0</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-[#64748B]">Your auto-approve limit</dt>
            <dd className="font-bold text-[#0A2540]">₹35,000</dd>
          </div>
          <div className="flex justify-between gap-3 border-t border-[#64748B]/15 pt-2">
            <dt className="text-[#64748B]">Hard constraints touched</dt>
            <dd className="font-bold text-emerald-600">None</dd>
          </div>
        </dl>
      </div>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-500">
        <span className="flex items-center gap-1 font-semibold text-emerald-700">
          <Icon className="text-[15px]" name="verified" />
          Executes without asking
        </span>
        <span className="font-mono">Over the limit it would wait</span>
      </div>
    </div>
  )
}

function ExecuteVisual() {
  const rows = [
    {
      icon: 'flight_takeoff',
      iconClass: 'text-[#38BDF8]',
      label: 'Replacement flight booked',
      status: 'CONFIRMED',
      statusClass: 'text-emerald-400 font-bold',
    },
    {
      icon: 'event_repeat',
      iconClass: 'text-amber-400',
      label: 'Hotel cancelled and rebooked',
      status: 'New check-in date',
      statusClass: 'text-slate-300',
    },
    {
      icon: 'receipt_long',
      iconClass: 'text-[#7DD3FC]',
      label: 'Both written to the timeline',
      status: 'Audit log',
      statusClass: 'text-slate-300',
    },
  ]

  return (
    <div className="flex h-full flex-col justify-between rounded-2xl border border-[#0F3254] bg-[#0A2540] p-6 font-mono text-xs text-white">
      <ul className="space-y-3">
        {rows.map((row) => (
          <li
            className="flex items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/10 p-3"
            key={row.label}
          >
            <span className="flex items-center gap-2.5">
              <Icon className={`text-[18px] ${row.iconClass}`} name={row.icon} />
              <span className="text-xs font-semibold text-white">{row.label}</span>
            </span>
            <span className={`shrink-0 text-[10px] ${row.statusClass}`}>{row.status}</span>
          </li>
        ))}
      </ul>
      <div className="mt-5 flex items-center justify-between border-t border-white/10 pt-3 text-[11px] text-slate-400">
        <span>Trip returns to RECOVERED</span>
        <span className="font-semibold text-emerald-400">Every step replayable</span>
      </div>
    </div>
  )
}
