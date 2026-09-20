import { Icon } from '../components/Icon'
import { Reveal } from '../components/Reveal'

const EYEBROW =
  'mb-3 inline-flex items-center gap-1.5 rounded-full bg-[#E0F2FE] px-3 py-1 font-mono text-[11px] font-bold uppercase text-[#0284C7] transition-colors group-hover:bg-[#0284C7] group-hover:text-white'

const CARD =
  'group flex flex-col justify-between rounded-2xl border border-[#64748B]/20 bg-[#F8FAFC] p-8 shadow-sm transition-all duration-300 hover:border-[#0284C7]/60 hover:shadow-md'

export function Features() {
  return (
    <section className="w-full bg-white px-6 py-24 md:px-10" id="features">
      <div className="mx-auto max-w-[1280px]">
        <Reveal className="mb-16 max-w-3xl">
          <span className="mb-2 block font-mono text-[12px] font-bold uppercase tracking-wider text-[#0284C7]">
            What is built
          </span>
          <h2 className="mb-4 font-display text-[38px] leading-[50px] tracking-tight text-[#0A2540] sm:text-[42px]">
            An agent that shows its working.
          </h2>
          <p className="text-base text-[#64748B] sm:text-lg">
            Four things the demo actually does. Anything not on this list is not in the build.
          </p>
        </Reveal>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
          <Reveal className={`${CARD} relative overflow-hidden md:col-span-7`}>
            <div className="z-10 max-w-md">
              <span className={EYEBROW}>
                <span className="size-1.5 animate-ping rounded-full bg-[#0284C7] group-hover:bg-white" />
                Monitoring
              </span>
              <h3 className="mb-3 text-2xl font-bold text-[#0A2540]">
                Scheduled polling that survives a restart
              </h3>
              <p className="text-sm leading-relaxed text-[#64748B]">
                Each flight carries its own next-check time in the database, so the monitor is
                resumable by construction — kill the process and it picks up where it stopped. The
                cadence tightens as departure approaches, which is what keeps a 500-call monthly
                budget viable.
              </p>
            </div>
            <RouteVisual />
          </Reveal>

          <Reveal className={`${CARD} md:col-span-5`} delayMs={100}>
            <div>
              <span className={EYEBROW}>Policy</span>
              <h3 className="mb-3 text-2xl font-bold text-[#0A2540]">
                Rejections you can read and argue with
              </h3>
              <p className="mb-6 text-sm leading-relaxed text-[#64748B]">
                Every option thrown out is kept, with the constraint it broke written in plain
                language. The reason the agent said no is on screen next to the reason it said yes.
              </p>
            </div>
            <ul className="flex flex-col gap-3 rounded-xl border border-[#64748B]/20 bg-white p-4 transition-colors group-hover:border-[#0284C7]/30">
              <PolicyRow
                icon="block"
                iconClass="text-red-600"
                label="Two stops"
                value="OVER 1-STOP LIMIT"
                valueClass="text-red-600"
              />
              <PolicyRow
                icon="schedule"
                iconClass="text-red-600"
                label="Arrives 11:20 local"
                value="PAST 09:00 DEADLINE"
                valueClass="text-red-600"
              />
              <PolicyRow
                icon="check_circle"
                iconClass="text-emerald-600"
                label="Rank 1 · departs 19:40"
                value="SCORE 98.4"
                valueClass="text-emerald-600"
              />
            </ul>
          </Reveal>

          <Reveal className={`${CARD} md:col-span-5`} delayMs={200}>
            <div>
              <span className={EYEBROW}>Hotels</span>
              <h3 className="mb-3 text-2xl font-bold text-[#0A2540]">
                The nights that move, moved for you
              </h3>
              <p className="mb-6 text-sm leading-relaxed text-[#64748B]">
                A later arrival can cost you a night. That cost is priced into the option before it
                is ranked, and if the plan goes ahead the booking is rebuilt at the new dates —
                cancel then rebook, because the hotel API has no date-change call.
              </p>
            </div>
            <div className="flex items-center justify-between gap-4 rounded-xl border border-[#64748B]/20 bg-white p-4 transition-colors group-hover:border-[#0284C7]/30">
              <div className="flex items-center gap-3">
                <span className="flex size-10 items-center justify-center rounded-lg bg-[#E0F2FE] text-[#0284C7] shadow-sm transition-transform group-hover:scale-105">
                  <Icon className="text-[20px]" name="event_repeat" />
                </span>
                <div>
                  <span className="block text-xs font-semibold text-[#0A2540]">
                    Check-in moved to the 14th
                  </span>
                  <span className="font-mono text-[11px] text-[#64748B]">
                    Cancelled and rebooked in one step
                  </span>
                </div>
              </div>
              <span className="shrink-0 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 font-mono text-xs font-semibold text-amber-700">
                +1 night
              </span>
            </div>
          </Reveal>

          <Reveal className={`${CARD} md:col-span-7`} delayMs={300}>
            <div>
              <span className={EYEBROW}>Transparency</span>
              <h3 className="mb-3 text-2xl font-bold text-[#0A2540]">
                A live timeline, not a status word
              </h3>
              <p className="mb-6 text-sm leading-relaxed text-[#64748B]">
                Every stage appends to the trip's audit log as it happens, and the dashboard
                receives each entry over a WebSocket. You can also paste a booking confirmation and
                have it parsed into a trip.
              </p>
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <ChannelCard
                body="DETECTED → PLANNING → EVALUATED → EXECUTED"
                dotClass="bg-[#0284C7]"
                hoverClass="hover:border-[#0284C7]/50"
                icon="timeline"
                title="Streamed as it runs"
              />
              <ChannelCard
                body="Paste a confirmation email, get a trip"
                dotClass="bg-[#0A2540]"
                hoverClass="hover:border-[#0A2540]/50"
                icon="content_paste"
                title="Booking import"
              />
            </div>
          </Reveal>
        </div>

        <Reveal className="story-film">
          <video controls muted playsInline preload="metadata">
            <source src="/assets/flight-story.mp4" type="video/mp4" />
          </video>
          <div>
            <p className="eyebrow">From cabin to control room</p>
            <h3>One continuous recovery story.</h3>
            <p>The film is illustrative. The product surfaces below it use a simulated disruption feed, deterministic providers, and sandbox booking.</p>
          </div>
        </Reveal>
      </div>
    </section>
  )
}

function PolicyRow({
  icon,
  iconClass,
  label,
  value,
  valueClass,
}: {
  icon: string
  iconClass: string
  label: string
  value: string
  valueClass: string
}) {
  return (
    <li className="flex items-center justify-between gap-3 rounded-lg border border-[#64748B]/15 bg-[#F8FAFC] p-3">
      <span className="flex items-center gap-2">
        <Icon className={`text-[20px] ${iconClass}`} name={icon} />
        <span className="text-xs font-semibold text-[#0A2540]">{label}</span>
      </span>
      <span className={`shrink-0 font-mono text-[11px] font-semibold ${valueClass}`}>{value}</span>
    </li>
  )
}

function ChannelCard({
  icon,
  title,
  body,
  dotClass,
  hoverClass,
}: {
  icon: string
  title: string
  body: string
  dotClass: string
  hoverClass: string
}) {
  return (
    <div
      className={`flex items-center gap-3 rounded-xl border border-[#64748B]/20 bg-white p-3.5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 ${hoverClass}`}
    >
      <span
        className={`flex size-8 shrink-0 items-center justify-center rounded-full text-white ${dotClass}`}
      >
        <Icon className="text-[16px]" name={icon} />
      </span>
      <span className="min-w-0">
        <span className="block text-xs font-semibold text-[#0A2540]">{title}</span>
        <span className="block truncate font-mono text-[11px] text-[#64748B]">{body}</span>
      </span>
    </div>
  )
}

/**
 * The cancelled leg in red, the replacement in blue, under a sweeping beam.
 * Abstract on purpose — there is no map SDK and no position data behind it, so
 * it carries no airport, no coordinates and no reading anyone could take
 * literally.
 */
function RouteVisual() {
  const rings = ['size-24', 'size-48', 'size-72', 'size-96 border-dashed']

  return (
    <div className="relative mt-8 flex h-64 w-full items-center justify-center overflow-hidden rounded-xl border border-[#0A2540] bg-[#0A2540]">
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 opacity-40">
        {rings.map((ring) => (
          <div
            className={`absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#0284C7]/30 ${ring}`}
            key={ring}
          />
        ))}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(2,132,199,0.2),rgba(10,37,64,0.8),#06182B)]" />
      </div>

      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 flex items-center justify-center"
      >
        <div className="animate-radar-beam flex size-[440px] items-center justify-center">
          <div
            className="h-1/2 w-1/2 origin-bottom-right"
            style={{
              background:
                'conic-gradient(from 0deg at 100% 100%, rgba(2,132,199,0.45) 0deg, rgba(2,132,199,0.08) 35deg, transparent 65deg)',
            }}
          />
        </div>
      </div>

      <svg
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 size-full"
        viewBox="0 0 500 250"
      >
        <path
          d="M 80 200 Q 180 140 240 120"
          fill="none"
          opacity="0.9"
          stroke="#EF4444"
          strokeDasharray="4 4"
          strokeWidth="2"
        />
        <circle cx="80" cy="200" fill="#EF4444" r="4" />
        <path
          className="animate-dash-route"
          d="M 240 120 Q 340 70 420 50"
          fill="none"
          filter="drop-shadow(0 0 8px #0284C7)"
          stroke="#0284C7"
          strokeWidth="3"
        />
        <circle cx="420" cy="50" fill="#0284C7" r="5" />
        <circle className="animate-ping" cx="240" cy="120" fill="#EF4444" opacity="0.5" r="6" />
        <circle cx="240" cy="120" fill="#ffffff" r="3" />
        <g transform="translate(350, 75) rotate(-22)">
          <path d="M0 -7 L4 4 L-4 4 Z" fill="#ffffff" />
          <circle
            className="animate-ping"
            cx="0"
            cy="0"
            fill="none"
            opacity="0.8"
            r="12"
            stroke="#38BDF8"
            strokeWidth="1.5"
          />
        </g>
      </svg>

      <div className="absolute left-6 top-4 flex items-center gap-2 rounded-xl border border-white/10 bg-[#06182B]/90 px-3.5 py-2 shadow-lg backdrop-blur-md transition-transform duration-200 group-hover:translate-x-1">
        <span className="relative flex size-2">
          <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex size-2 rounded-full bg-emerald-400" />
        </span>
        <span>
          <span className="block text-xs font-semibold text-white">ORIGINAL LEG CANCELLED</span>
          <span className="font-mono text-[10px] text-slate-300">Replacement ranked first</span>
        </span>
      </div>

      <div className="absolute bottom-4 right-6 flex items-center gap-2 rounded-xl border border-white/10 bg-[#06182B]/90 px-3.5 py-2 shadow-lg backdrop-blur-md transition-transform duration-200 group-hover:-translate-x-1">
        <Icon className="animate-pulse text-[15px] text-[#0284C7]" name="schedule" />
        <span>
          <span className="block text-xs font-semibold text-white">NEXT CHECK IN 15 MIN</span>
          <span className="font-mono text-[10px] text-slate-300">Stored on the flight row</span>
        </span>
      </div>
    </div>
  )
}
