import { Icon } from '../components/Icon'
import { useReveal } from '../lib/useReveal'

/**
 * What ATC is actually wired to, and under what guard.
 *
 * This slot usually holds logos and a user count. There are no users and no
 * logo rights, so it holds the integration list and the quota rule instead —
 * the two facts a judge would otherwise have to ask for.
 */
const INTEGRATIONS = [
  { icon: 'radar', label: 'AeroDataBox', role: 'Flight status' },
  { icon: 'flight_takeoff', label: 'Duffel', role: 'Search & book, test mode' },
  { icon: 'hotel', label: 'LiteAPI / Nuitee', role: 'Hotel lifecycle, sandbox' },
  { icon: 'bolt', label: 'Groq', role: 'Plan narration, optional' },
]

export function TrustStrip() {
  const [ref, visible] = useReveal<HTMLElement>()

  return (
    <section
      className="reveal-on-scroll w-full border-y border-[#64748B]/15 bg-white px-6 py-8 md:px-10"
      data-visible={visible}
      ref={ref}
    >
      <div className="mx-auto flex max-w-[1280px] flex-col items-start justify-between gap-6 md:flex-row md:items-center">
        <div className="max-w-md">
          <p className="text-sm font-semibold text-[#0A2540]">
            Real decision logic, deterministic mock providers
          </p>
          <p className="mt-1 text-xs leading-relaxed text-[#64748B]">
            Production adapters are quota-aware; this MVP ships with{' '}
            <span className="font-mono text-[#0A2540]">DEMO_MODE=true</span> so rehearsals are
            stable and never claim live airline write access.
          </p>
        </div>

        <ul className="flex flex-wrap items-center gap-3">
          {INTEGRATIONS.map((item) => (
            <li
              className="flex items-center gap-2 rounded-lg border border-[#64748B]/20 bg-[#F8FAFC] px-3 py-2 transition-all duration-200 hover:-translate-y-0.5 hover:border-[#0284C7] hover:shadow-sm"
              key={item.label}
            >
              <Icon className="text-[18px] text-[#0284C7]" name={item.icon} />
              <span>
                <span className="block text-xs font-semibold text-[#0A2540]">{item.label}</span>
                <span className="block font-mono text-[10px] text-[#64748B]">{item.role}</span>
              </span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
