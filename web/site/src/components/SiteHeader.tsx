import { useEffect, useRef } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { appLink } from '../lib/links'
import { scrollProgress } from '../lib/progress'

const NAV_LINKS = [
  { to: '/', label: 'Home' },
  { to: '/how-it-works', label: 'How it works' },
  { to: '/faq', label: 'FAQ' },
]

export function SiteHeader() {
  const headerRef = useRef<HTMLElement>(null)
  const barRef = useRef<HTMLDivElement>(null)
  const { pathname } = useLocation()

  useEffect(() => {
    const update = () => {
      const progress = scrollProgress(window.scrollY, document.documentElement.scrollHeight, window.innerHeight)
      if (barRef.current) barRef.current.style.transform = `scaleX(${progress})`
      headerRef.current?.classList.toggle('is-scrolled', window.scrollY > 20)
    }
    let queued = false
    const schedule = () => {
      if (queued) return
      queued = true
      requestAnimationFrame(() => { queued = false; update() })
    }
    const observer = new ResizeObserver(schedule)
    observer.observe(document.documentElement)
    void document.fonts?.ready.then(schedule)
    update()
    window.addEventListener('scroll', schedule, { passive: true })
    window.addEventListener('resize', schedule, { passive: true })
    return () => { observer.disconnect(); window.removeEventListener('scroll', schedule); window.removeEventListener('resize', schedule) }
  }, [pathname])

  return (
    <header className="site-header" ref={headerRef}>
      <div className="site-nav">
        <Link aria-label="ATC home" className="brand" to="/">
          <img alt="" src="/assets/atc-logo.png" /><span>ATC</span><small>Concierge</small>
        </Link>
        <nav aria-label="Main navigation">
          {NAV_LINKS.map(({ to, label }) => <NavLink className={({ isActive }) => isActive ? 'active' : ''} key={to} to={to}>{label}</NavLink>)}
        </nav>
        <div className="header-actions">
          <a className="login-link" href={appLink('/login')}>Log in</a>
          <a className="button-primary" href={appLink('/signup')}>Get started</a>
        </div>
      </div>
      <div className="progress-track"><div className="progress-line" ref={barRef} /></div>
    </header>
  )
}
