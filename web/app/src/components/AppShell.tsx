import type { ReactNode } from 'react'
import { ProfileMenu } from './ProfileMenu'
import type { Trip } from '../types'

interface AppShellProps {
  children: ReactNode
  /** Absent until the first snapshot lands — the header renders without the menu. */
  trip?: Trip
}

export function AppShell({ children, trip }: AppShellProps) {
  const siteUrl = import.meta.env.VITE_SITE_URL

  return (
    <div className="app-theme min-h-screen bg-background text-on-surface">
      <header className="sticky top-0 z-20 border-b border-white/10 bg-navy text-white shadow-card">
        <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-8" aria-label="Product">
          <a className="flex items-center gap-3 font-semibold" href={siteUrl}>
            <span className="grid size-9 place-items-center rounded-lg bg-sky font-mono text-sm">ATC</span>
            <span>
              <span className="block leading-none">Travel Concierge</span>
              <span className="mt-1 hidden font-mono text-[9px] font-medium uppercase tracking-[0.2em] text-white/60 sm:block">
                Autonomous recovery
              </span>
            </span>
          </a>
          <div className="flex items-center gap-3">
            <span className="hidden rounded-full border border-white/15 bg-white/10 px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.16em] text-white/80 sm:inline-flex">
              Simulated feed
            </span>
            <span className="hidden items-center gap-2 rounded-full bg-emerald-400/10 px-3 py-1.5 text-xs font-semibold text-emerald-200 sm:flex">
              <span className="relative flex size-2" aria-hidden="true">
                <span className="ping-ring absolute inline-flex size-2 rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex size-2 rounded-full bg-emerald-400" />
              </span>
              Monitoring
            </span>
            {trip && <ProfileMenu constraints={trip.constraints} travellerName={trip.traveller_name} />}
          </div>
        </nav>
      </header>
      {/* overflow-x-clip: a tooltip anchored near the right edge must not be able to
          widen the page. `clip` leaves the vertical axis visible, so tooltips still
          escape upwards out of their card. */}
      <main className="mx-auto max-w-7xl overflow-x-clip px-4 py-8 sm:px-8 sm:py-12">{children}</main>
    </div>
  )
}
