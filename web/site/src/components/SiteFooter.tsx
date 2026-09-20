import { Icon } from './Icon'

const appUrl = import.meta.env.VITE_APP_URL

/**
 * Only destinations that exist. The usual product/company/legal columns would
 * be a dozen links to pages nobody has written, which on a page whose whole
 * argument is "we show our working" is the wrong first impression.
 */
const COLUMNS = [
  {
    heading: 'On this page',
    links: [
      { label: 'How the agent runs', href: '#how-it-works' },
      { label: 'What is built', href: '#features' },
      { label: 'What is not built', href: '#faq' },
    ],
  },
  {
    heading: 'Try it',
    links: [
      { label: 'Open the dashboard', href: appUrl },
      { label: 'Simulate a cancellation', href: appUrl },
    ],
  },
]

export function SiteFooter() {
  return (
    <footer className="w-full border-t border-white/10 bg-[#0A2540] text-white">
      <div className="mx-auto w-full max-w-[1280px] px-6 pb-12 pt-16 md:px-10">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-12">
          <div className="flex flex-col gap-4 pr-0 md:col-span-5 md:pr-12">
            <div className="flex items-center gap-3">
              <span className="flex size-9 items-center justify-center rounded-xl bg-[#0284C7] text-white">
                <Icon className="text-[20px]" name="connecting_airports" />
              </span>
              <span className="text-lg font-bold tracking-tight text-white">ATC</span>
            </div>
            <p className="max-w-md text-sm leading-relaxed text-slate-400">
              Autonomous travel-disruption concierge detecting flight cancellations and resolving
              itineraries in real time.
            </p>
          </div>
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 md:col-span-7">
            {COLUMNS.map((column) => (
              <nav aria-label={column.heading} className="flex flex-col gap-3" key={column.heading}>
                <span className="text-sm font-semibold text-white">{column.heading}</span>
                {column.links.map((link) => (
                  <a
                    className="text-sm text-slate-400 transition-colors hover:text-[#0284C7]"
                    href={link.href}
                    key={link.label}
                  >
                    {link.label}
                  </a>
                ))}
              </nav>
            ))}
          </div>
        </div>
        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-white/10 pt-8 sm:flex-row">
          <p className="text-xs text-slate-400">
            © {new Date().getFullYear()} Autonomous Travel-Disruption Concierge (ATC). Built for the
            hackathon demo.
          </p>
          <p className="flex items-center gap-2 font-mono text-xs text-slate-400">
            <span className="inline-block size-2 animate-pulse rounded-full bg-emerald-400" />
            Demo mode — mock providers
          </p>
        </div>
      </div>
    </footer>
  )
}
