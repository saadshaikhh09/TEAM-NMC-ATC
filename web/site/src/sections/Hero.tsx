import { Icon } from '../components/Icon'
import { appLink } from '../lib/links'

/**
 * Above the fold: the claim, the two calls to action, and a mocked-up console
 * showing a cancellation already resolved. The mockup is illustrative — it is
 * the product's promise rendered as a still, not live data.
 */
export function Hero() {
  return (
    <section
      className="relative w-full overflow-hidden bg-gradient-to-b from-[#F0F5FA] via-[#F8FAFC] to-[#F8FAFC] px-6 pb-24 pt-36 md:px-10"
      id="top"
    >
      <div
        className="pointer-events-none absolute -top-40 left-1/2 h-[750px] w-[1100px] -translate-x-1/2 animate-pulse rounded-full bg-gradient-to-br from-[#0284C7]/15 via-[#0A2540]/10 to-transparent opacity-70 blur-3xl"
        style={{ animationDuration: '8s' }}
      />

      <div className="relative z-10 mx-auto flex max-w-[1280px] flex-col items-center text-center">
        <p className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#64748B]/20 bg-white px-4 py-1.5 shadow-sm transition-all duration-300 hover:scale-[1.02] hover:border-[#0284C7]/40 hover:shadow">
          <span className="relative flex size-2.5">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-[#0284C7] opacity-75" />
            <span className="relative inline-flex size-2.5 rounded-full bg-[#0284C7]" />
          </span>
          <span className="font-mono text-[12px] font-medium tracking-wide text-[#0A2540]">
            Tiered flight polling • Policy-gated rebooking
          </span>
        </p>

        <h1 className="mb-5 max-w-4xl font-display text-[42px] leading-[48px] tracking-tight text-[#0A2540] sm:text-[56px] sm:leading-[64px]">
          Never manage a cancelled <br className="hidden sm:inline" />
          <span className="font-normal italic text-[#0284C7] transition-colors duration-300 hover:text-[#0369A1]">
            flight alone
          </span>{' '}
          again.
        </h1>

        <p className="mx-auto mb-8 max-w-2xl text-base leading-relaxed text-[#64748B] sm:text-lg">
          ATC polls your flights on a tiered schedule, detects a cancellation or delay, and works
          out a replacement against your own constraints — showing you every option it rejected and
          why. Under your auto-approve limit it rebooks on its own; over it, it waits for you.
        </p>

        <div className="mb-16 flex w-full flex-col items-center justify-center gap-4 sm:w-auto sm:flex-row">
          <a
            className="shimmer-btn group inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#0284C7] px-8 py-3.5 text-base font-semibold text-white shadow-md shadow-[#0284C7]/25 transition-all duration-150 hover:-translate-y-0.5 hover:bg-[#0369A1] hover:shadow-lg hover:shadow-[#0284C7]/30 active:scale-[0.97] sm:w-auto"
            href={appLink('/signup')}
          >
            <span>Open the dashboard</span>
            <Icon
              className="text-[18px] transition-transform duration-200 group-hover:translate-x-1"
              name="arrow_forward"
            />
          </a>
          <a
            className="group inline-flex w-full items-center justify-center gap-2 rounded-xl border border-[#64748B]/25 bg-white px-7 py-3.5 text-base font-semibold text-[#0A2540] shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:border-[#64748B]/40 hover:bg-[#F0F5FA] hover:shadow-md active:scale-[0.97] sm:w-auto"
            href="/how-it-works"
          >
            <Icon
              className="text-[18px] text-[#0284C7] transition-transform duration-200 group-hover:scale-110"
              name="play_circle"
            />
            <span>See how it works</span>
          </a>
        </div>

        <HeroMockup />
      </div>
    </section>
  )
}

function HeroMockup() {
  return (
    <div className="mt-2 w-full max-w-[1080px]">
      <div className="animate-float-dashboard relative overflow-hidden rounded-2xl bg-white text-left shadow-[0_25px_50px_-12px_rgba(10,37,64,0.16),0_0_0_1px_rgba(100,116,139,0.16)] transition-shadow duration-500 hover:shadow-[0_30px_60px_-10px_rgba(10,37,64,0.22),0_0_0_1px_rgba(2,132,199,0.3)]">
        {/* Browser chrome */}
        <div className="flex items-center justify-between border-b border-[#0A2540] bg-[#0A2540] px-5 py-3 text-white">
          <div className="flex items-center gap-2">
            <span className="size-3 rounded-full bg-[#EF4444]" />
            <span className="size-3 rounded-full bg-[#F59E0B]" />
            <span className="size-3 rounded-full bg-[#10B981]" />
          </div>
          <div className="hidden w-80 items-center justify-center gap-2 rounded-full bg-white/10 px-4 py-1 font-mono text-[12px] text-slate-200 shadow-inner sm:flex">
            <Icon className="animate-pulse text-[14px] text-[#0284C7]" name="lock" />
            <span className="tracking-tight">concierge.atc.travel/monitor/BA-143</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <Icon className="text-[16px]" name="sync" />
            <Icon className="text-[16px]" name="tune" />
          </div>
        </div>

        <div className="flex flex-col gap-6 bg-white p-6 md:p-8">
          {/* Disruption banner */}
          <div className="flex flex-col justify-between gap-3 rounded-xl border border-red-200 bg-[#FEF2F2] p-4 sm:flex-row sm:items-center">
            <div className="flex items-center gap-3">
              <span
                className="flex size-10 shrink-0 animate-pulse items-center justify-center rounded-lg bg-red-600 text-white shadow-sm"
                style={{ animationDuration: '2.5s' }}
              >
                <Icon className="text-[20px]" name="warning" />
              </span>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-base font-semibold text-red-900">
                    Flight BA 143 cancelled by airline
                  </span>
                  <span className="rounded-full border border-red-200 bg-white px-2 py-0.5 font-mono text-[11px] font-semibold uppercase text-red-700">
                    Gate 24C
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-red-700">
                  Picked up on the scheduled status poll • Trip moved to DISRUPTED and the recovery
                  plan started
                </p>
              </div>
            </div>
            <span className="shrink-0 rounded-lg border border-red-200 bg-white px-3 py-1.5 font-mono text-[12px] font-semibold text-red-800">
              Detected 3h 40m before departure
            </span>
          </div>

          {/* Agent telemetry bar */}
          <div className="flex flex-col justify-between gap-4 rounded-xl bg-[#0A2540] p-4 text-white md:flex-row md:items-center">
            <div className="flex items-center gap-3">
              <span className="flex size-9 items-center justify-center rounded-xl bg-[#0284C7] text-white shadow-sm">
                {/* A 12s rotation reads as "working"; a 1s spinner reads as "stuck". */}
                <Icon
                  className="animate-spin text-[18px] [animation-duration:12s]"
                  name="auto_awesome"
                />
              </span>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-semibold text-white">Recovery planner</span>
                  <span className="relative flex size-2.5">
                    <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-80" />
                    <span className="relative inline-flex size-2.5 rounded-full bg-emerald-400" />
                  </span>
                  <span className="font-mono text-[11px] font-medium uppercase tracking-wider text-emerald-300">
                    Auto-approved
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-slate-300">
                  Evaluated 6 options, rejected 3 on your constraints, ranked the rest on arrival
                  time, fare and stops
                </p>
              </div>
            </div>
            <span className="shrink-0 rounded-md border border-white/15 bg-white/10 px-3 py-1 font-mono text-[11px] text-slate-300">
              UNDER AUTO-APPROVE LIMIT
            </span>
          </div>

          {/* Resolution options */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div className="pulse-glow-border relative overflow-hidden rounded-xl border-2 border-[#0284C7] bg-[#F8FAFC] p-5 shadow-sm transition-all duration-300 hover:shadow-md">
              <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-[#0284C7] via-[#38BDF8] to-[#0284C7]" />
              <div className="mb-4 flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="flex size-10 items-center justify-center rounded-lg bg-[#0A2540] text-sm font-bold text-white">
                    VS
                  </span>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-base font-semibold text-[#0A2540]">
                        Virgin Atlantic • VS 302
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 font-mono text-[11px] font-semibold text-emerald-700">
                        <span className="size-1.5 animate-pulse rounded-full bg-emerald-500" />
                        Rank 1 • Rebooked
                      </span>
                    </div>
                    <span className="text-xs text-[#64748B]">
                      London Heathrow (LHR) → New York (JFK)
                    </span>
                  </div>
                </div>
                <div className="shrink-0 text-right">
                  <span className="text-lg font-bold text-[#0284C7]">+₹0</span>
                  <span className="block font-mono text-[10px] text-[#64748B]">
                    Net change vs original
                  </span>
                </div>
              </div>
              <dl className="mb-4 grid grid-cols-3 gap-2 rounded-lg border border-[#64748B]/15 bg-white px-3 py-3 text-center">
                <MockStat label="New departure" value="19:40 GMT" />
                <MockStat label="Cabin" value="Business" />
                <MockStat label="Arrives later by" value="18 min" valueClass="text-emerald-600" />
              </dl>
              <div className="flex flex-wrap items-center justify-between gap-2 border-t border-[#64748B]/15 pt-2">
                <span className="flex items-center gap-2 font-mono text-xs text-[#64748B]">
                  <Icon className="text-[16px] text-emerald-600" name="check_circle" />
                  Booked and written to the trip timeline
                </span>
                <span className="rounded bg-[#E0F2FE] px-2 py-0.5 font-mono text-[11px] font-semibold text-[#0284C7]">
                  Score 98.4
                </span>
              </div>
            </div>

            <div className="rounded-xl border border-[#64748B]/20 bg-[#F8FAFC] p-5 opacity-85 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-[#64748B]/40 hover:opacity-100">
              <div className="mb-4 flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="flex size-10 items-center justify-center rounded-lg bg-[#E2E8F0] text-sm font-bold text-[#0A2540]">
                    AA
                  </span>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-base font-semibold text-[#0A2540]">
                        American Airlines • AA 105
                      </span>
                      <span className="rounded-full border border-[#64748B]/20 bg-white px-2 py-0.5 font-mono text-[11px] text-[#64748B]">
                        Rank 2
                      </span>
                    </div>
                    <span className="text-xs text-[#64748B]">
                      London Heathrow (LHR) → New York (JFK)
                    </span>
                  </div>
                </div>
                <div className="shrink-0 text-right">
                  <span className="text-base font-semibold text-[#0A2540]">+₹2,400</span>
                  <span className="block font-mono text-[10px] text-[#64748B]">
                    Net change vs original
                  </span>
                </div>
              </div>
              <dl className="mb-4 grid grid-cols-3 gap-2 rounded-lg border border-[#64748B]/15 bg-white px-3 py-3 text-center">
                <MockStat label="Departure" value="20:15 GMT" />
                <MockStat label="Cabin" value="Business" />
                <MockStat label="Arrives later by" value="45 min" valueClass="text-amber-600" />
              </dl>
              <div className="flex flex-wrap items-center justify-between gap-2 border-t border-[#64748B]/15 pt-2">
                <span className="text-xs text-[#64748B]">Passed every constraint, ranked lower</span>
                <span className="font-mono text-[11px] text-[#64748B]">Score 91.2</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MockStat({
  label,
  value,
  valueClass = 'text-[#0A2540]',
}: {
  label: string
  value: string
  valueClass?: string
}) {
  return (
    <div>
      <dt className="block font-mono text-[10px] uppercase text-[#64748B]">{label}</dt>
      <dd className={`font-mono text-[13px] font-semibold ${valueClass}`}>{value}</dd>
    </div>
  )
}
