import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import type { Account } from '../services/api'
import { ProfileMenu } from './ProfileMenu'

export function AppShell({ children, account, onLogout }: { children: ReactNode; account: Account; onLogout: () => Promise<void> }) {
  const siteUrl = import.meta.env.VITE_SITE_URL ?? 'http://localhost:5173'
  return (
    <div className="app-theme min-h-screen bg-background text-on-surface">
      <a className="app-skip-link" href="#app-main">Skip to content</a>
      <header className="app-header">
        <div className="app-nav">
          <a aria-label="ATC public website" className="app-brand" href={siteUrl}>
            <img alt="" src="/assets/atc-logo.png" /><span><b>ATC</b><small>Travel Concierge</small></span>
          </a>
          <nav aria-label="Application">
            <NavLink end to="/app">Overview</NavLink>
            <NavLink to="/app/trips">Trips</NavLink>
            <NavLink to="/app/trips/new">Add trip</NavLink>
          </nav>
          <div className="app-nav-right">
            <span className="demo-chip">Simulated feed</span>
            <ProfileMenu account={account} onLogout={onLogout} />
          </div>
        </div>
      </header>
      <main className="app-main" id="app-main">{children}</main>
      <nav aria-label="Mobile application navigation" className="mobile-nav">
        <NavLink end to="/app">Overview</NavLink><NavLink to="/app/trips">Trips</NavLink><NavLink to="/app/trips/new">Add trip</NavLink>
      </nav>
    </div>
  )
}
